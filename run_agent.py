"""运行 my_agent1 进行本地测试。"""

import argparse

from agent.my_agent1 import agent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread", default="test_thread_01")
    args = parser.parse_args()

    config = {"configurable": {"thread_id": args.thread}}

    print("=== Deep Agent 交互式对话 ===")
    print("输入 quit/exit/q 退出\n")

    while True:
        try:
            user_input = input("\n[用户] >>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        if not user_input:
            continue

        print("\n[Agent] >>>> ", end="", flush=True)

        inputs = {"messages": [{"role": "user", "content": user_input}]}

        full_response = ""
        try:
            for chunk in agent.stream(inputs, config=config, stream_mode="messages"):
                if isinstance(chunk, tuple) and len(chunk) == 2:
                    token, metadata = chunk
                    if hasattr(token, 'content') and token.content:
                        content_str = str(token.content)
                        if content_str:
                            print(content_str, end="", flush=True)
                            full_response += content_str
        except Exception as e:
            print(f"\n❌ 出错: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
