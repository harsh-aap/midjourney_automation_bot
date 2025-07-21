import argparse
from midjourney.core.main import ImageGenerator


def main():
    parser = argparse.ArgumentParser(
            description="Generate prompts for Midjourney bot")
    parser.add_argument('--date', '-d',
                        type=str,
                        help="Date for prompt generation (YYYY-MM-DD)")
    parser.add_argument('--category', '-c',
                        type=str,
                        help="Specific category (e.g., health, career)")
    parser.add_argument('--prompt', '-p',
                        type=str,
                        help="User-defined prompt to send directly")
    parser.add_argument('--desc', '-t',
                        type=str,
                        help="Description for prompt generation via OpenAI")

    args = parser.parse_args()

    # Determine mode of operation
    if args.prompt:
        print("📝 Custom Prompt Mode")
        print(f"➡ Prompt: {args.prompt}")
    elif args.desc:
        print("📜 Description Mode")
        print(f"➡ Desc: {args.desc}")
    elif args.category:
        print("📂 Category Mode")
        print(f"➡ Date: {args.date or 'today'}")
        print(f"➡ Category: {args.category}")
    else:
        print("📆 Date-Based Mode")
        print(f"➡ Date: {args.date or 'today'}")
        print("➡ Category: None")

    generator = ImageGenerator()

    # Push message to background queue
    generator.message_push(
        date=args.date,
        category=args.category,
        user_prompt=args.prompt,
        description=args.desc
    )

    # Wait for the message queue to process all prompts
    print("🕒 Waiting for prompts to be sent...")
    generator.message_queue.join()
    print("✅ All prompts processed successfully.")


if __name__ == "__main__":
    main()
