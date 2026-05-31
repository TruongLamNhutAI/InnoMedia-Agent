# file: graph.py
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import write_script_node, review_script_node, visual_prompt_node

# 1. HÀM ĐỊNH TUYẾN (ROUTER)
def router_script_approval(state: AgentState):
    """Đọc State và quyết định đường đi tiếp theo"""
    if state.get("script_approved") == True:
        return "visual_prompt_node" # Duyệt thì đi làm hình ảnh
    
    if state.get("retry_count", 0) >= 3:
        print("[HỆ THỐNG] Quá 3 lần viết lại. Dừng luồng để tránh treo hệ thống!")
        return END # Quá 3 bận thì ép dừng
    
    return "write_script_node" # Chưa duyệt và còn lượt thì vòng lại

# 2. LẮP RÁP ĐỒ THỊ
workflow = StateGraph(AgentState)

# Khai báo các điểm (Nodes)
workflow.add_node("write_script_node", write_script_node)
workflow.add_node("review_script_node", review_script_node)
workflow.add_node("visual_prompt_node", visual_prompt_node)

# Vẽ đường đi (Edges)
workflow.set_entry_point("write_script_node")
workflow.add_edge("write_script_node", "review_script_node")

# Cài đặt trạm kiểm soát (Conditional Edge) tại Node Review
workflow.add_conditional_edges(
    "review_script_node", 
    router_script_approval, 
    {
        "visual_prompt_node": "visual_prompt_node",
        "write_script_node": "write_script_node",
        END: END
    }
)

workflow.add_edge("visual_prompt_node", END)

# Đóng gói đồ thị
app = workflow.compile()

# ==========================================
# 3. CHẠY THỬ VỚI LLM THẬT
# ==========================================
if __name__ == "__main__":
    import json # Thêm thư viện này để format output 
    
    print("=== KHỞI ĐỘNG HỆ THỐNG INNOMEDIA-AGENT (LLM MODE) ===")
    
    # Khởi tạo Input ban đầu từ User
    initial_state = {
        "product_url": "Balo chống nước thời trang Hàn Quốc dành cho nam", # có thể thay bằng bất kỳ sản phẩm nào khác để test
        "retry_count": 0,
        "review_feedback": ""
    }
    
    # Biến để lưu lại kết quả của Node cuối cùng
    final_state = {}
    
    # Chạy đồ thị
    for output in app.stream(initial_state, config={"recursion_limit": 10}):
        # recursion_limit: Đảm bảo đồ thị không chạy lặp vô tận (safeguard của LangGraph)
        for node_name, state_update in output.items():
            # Update final_state liên tục để lấy kết quả sau cùng
            final_state.update(state_update) 
            
    print("\n=======================================================")
    print("=== KẾT QUẢ BÀN GIAO CHO MEDIA ENGINE (SERVICE 3) ===")
    print("=======================================================\n")
    
    if "visual_prompts" in final_state and final_state["visual_prompts"]:
        # In ra JSON để đem đi test
        print(json.dumps(final_state["visual_prompts"], indent=2, ensure_ascii=False))
    else:
        print("[THẤT BẠI] Hệ thống không thể xuất ra Visual Prompts. Hãy kiểm tra lại log.")