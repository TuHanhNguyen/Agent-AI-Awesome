import autogen
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from CSDL import get_inventory, get_inventory_declaration
from GuiEmail import send_mail, send_email_declaration
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Hàm này nối tất cả các tin nhắn do tác nhân "customer_support_agent" gửi,
# sau đó trả về dưới dạng một chuỗi.
def concat_assistant_messages(chat_messages):
   messages = ""
   for message in chat_messages:
      if message.get('name') == 'customer_support_agent':
        messages += message.get('content')
   return messages

@app.route('/run')
def spare_parts():
   # Lấy truy vấn (query) từ tham số GET trên URL
   query = request.args.get('query')

   # Gọi hàm initiate_chat_voiceflow để khởi tạo hội thoại dựa trên truy vấn
   messages = initiate_chat_voiceflow(query)

   # Trả về kết quả dạng JSON, trong đó "query" là nội dung tin nhắn của assistant
   return jsonify({"query": concat_assistant_messages(messages)})

def initiate_chat_voiceflow(query):
   # Khởi tạo hội thoại với user_proxy, đưa ra yêu cầu:
   # Yêu cầu: Trả về tình trạng sẵn có (availability) và giá (price) của linh kiện,
   # rồi gửi "TERMINATE".
   #
   # Prompt gốc tiếng Anh:
   # "Return the availability and price of the requested spare part and send 'TERMINATE'."
   # Dịch sang tiếng Việt tự nhiên:
   # "Hãy trả về thông tin về tình trạng sẵn có và giá của linh kiện được yêu cầu,
   # và sau đó gửi 'TERMINATE' để kết thúc."
   #
   # Yêu cầu định dạng đầu ra:
   # "Output Format: 'Availability: In stock \n Price:'"
   # Dịch sang tiếng Việt tự nhiên:
   # "Định dạng đầu ra: 'Availability: In stock \n Price:'"
   user_proxy.initiate_chat(
      manager,
      message = f"""
          Hãy trả về tình trạng sẵn có và giá của linh kiện yêu cầu, 
          sau đó gửi 'TERMINATE'.

          Yêu cầu: '{query}'

          Định dạng đầu ra: 'Availability: In stock \n Price:'
      """
   )

   messages = user_proxy.chat_messages[manager]

   return messages

@app.route('/', methods=['GET', 'POST'])
def index():
    # Trang chủ: khi khách hàng tải trang (GET) thì hiển thị form để nhập thông tin
    # Khi khách hàng gửi form (POST), thì lấy dữ liệu hình ảnh, email, thông điệp từ form
    # và khởi tạo hội thoại xử lý.
    if request.method == 'POST':
      image_url = request.form['image']
      customer_email = request.form['email']
      customer_message = request.form['message']

      # Gọi hàm initiate_chat để bắt đầu quy trình phân tích thiệt hại,
      # kiểm tra tồn kho, và gửi email báo giá
      initiate_chat(image_url, customer_email, customer_message)

      return render_template('result.html')
    else:
       return render_template('index.html')

# Đọc cấu hình mô hình từ file OAI_CONFIG_LIST (đây là chức năng nội bộ của autogen)
config_list = autogen.config_list_from_json('OAI_CONFIG_LIST')

config_list_v4 = autogen.config_list_from_json('OAI_CONFIG_LIST', filter_dict={
    "model": ["gpt-4o"]
})

# Hàm kiểm tra thông điệp kết thúc (TERMINATE)
# Nếu thông điệp có từ "TERMINATE" trong content thì kết thúc
def is_termination_msg(data):
    has_content = "content" in data and data["content"] is not None
    return has_content and "TERMINATE" in data["content"]

# user_proxy: Tác nhân đại diện cho người dùng, với chế độ input từ con người là "NEVER"
# nghĩa là không yêu cầu đầu vào thủ công.
# Các hàm get_inventory, send_mail được gán vào function_map để assistant có thể gọi.
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    system_message="You're the boss",  # Hệ thống: "Bạn là sếp" -> cho tác nhân biết vai trò.
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    function_map={"get_inventory": get_inventory, "send_mail": send_mail},
    code_execution_config={"use_docker": False}
)

# damage_analyst: Tác nhân phân tích hình ảnh.
# Nhiệm vụ: Mô tả chính xác nội dung ảnh, không suy đoán.
damage_analyst = MultimodalConversableAgent(
    name="damage_analyst",
    system_message="""
      Với vai trò là chuyên viên phân tích hư hại, nhiệm vụ của bạn là mô tả chính xác nội dung hình ảnh được cung cấp.
      Chỉ phản hồi dựa trên thông tin hiển thị trong ảnh, không thêm giả định hoặc thông tin không có trong ảnh.
    """,
    llm_config={"config_list": config_list_v4, "max_tokens": 300}
)

# inventory_manager: Tác nhân quản lý tồn kho.
# Nhiệm vụ: Cung cấp thông tin về tình trạng sẵn có và giá cả. Hiện tại giả định tất cả đều có sẵn.
inventory_manager = autogen.AssistantAgent(
    name="inventory_mananager",
    system_message="""
      Với vai trò là quản lý tồn kho, bạn cung cấp thông tin về tình trạng sẵn có và giá linh kiện.
      Tạm thời, hãy phản hồi rằng mọi thứ đều có sẵn.
    """,
    llm_config={"config_list": config_list,
                "functions": [get_inventory_declaration]}
)

# customer_support_agent: Tác nhân hỗ trợ khách hàng.
# Nhiệm vụ: Soạn và gửi email sau khi đã xác nhận tồn kho và giá cả.
# Khi hoàn thành, gửi "TERMINATE".
customer_support_agent = autogen.AssistantAgent(
    name="customer_support_agent",
    system_message="""
      Là nhân viên hỗ trợ khách hàng, bạn chịu trách nhiệm soạn và gửi email 
      sau khi đã xác nhận tồn kho và giá. 
      Khi hoàn thành, hãy gửi "TERMINATE".
    """,
    llm_config={"config_list": config_list, "functions": [send_email_declaration]}
)

# groupchat: Nhóm chat gồm 4 tác nhân: user_proxy, inventory_manager, customer_support_agent, damage_analyst
groupchat = autogen.GroupChat(
    agents=[user_proxy, inventory_manager, customer_support_agent, damage_analyst], messages=[]
)

# manager: Quản lý nhóm chat, cung cấp cấu hình mô hình
manager = autogen.GroupChatManager(
    groupchat=groupchat, llm_config={"config_list": config_list}
)

def initiate_chat(image_url, customer_email, customer_message):
  # Khởi tạo hội thoại với user_proxy:
  # Quy trình:
  # 1. damage_analyst nhận diện hãng xe, linh kiện hỏng qua ảnh và mô tả của khách
  # 2. inventory_manager kiểm tra tồn kho và giá
  # 3. customer_support_agent soạn và gửi email báo giá
  #
  # Thông điệp được gửi đến user_proxy, yêu cầu thực hiện các bước trên.

  user_proxy.initiate_chat(
      manager, message=f"""
        Quy trình xử lý:

        Bước 1: Chuyên viên phân tích hư hại (Damage Analyst) xác định hãng xe và linh kiện được yêu cầu
        (có bộ phận nào bị hỏng hoặc thiếu?) dựa trên tin nhắn khách hàng và hình ảnh.

        Bước 2: Quản lý tồn kho (Inventory Manager) xác minh linh kiện trong cơ sở dữ liệu.

        Bước 3: Nhân viên hỗ trợ khách hàng (Customer Support Agent) soạn và gửi email phản hồi kèm giá cho từng linh kiện, nhớ format sao cho chuyên nghiệp như Toyota Mỹ.

        Thông điệp từ khách hàng: '{customer_message}'
        Email của khách hàng: '{customer_email}'
        Tham chiếu hình ảnh: '{image_url}'
      """
  )

if __name__ == '__main__':
    app.run(debug=True)
