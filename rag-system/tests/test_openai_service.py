from app.llm.openai_service import generate_compliance_answer


def test_generate_compliance_answer_builds_prompt_from_chunks(fake_openai):
    fake_openai.reply = "Retention is 30 days (Clause 2)."

    answer = generate_compliance_answer(
        "How long is data retained?",
        [{"text": "Processor acts on instructions."}, {"text": "Data is kept for 30 days."}]
    )

    assert answer == "Retention is 30 days (Clause 2)."
    assert len(fake_openai.calls) == 1

    call = fake_openai.calls[0]
    assert call["model"] == "gpt-4.1"
    user_prompt = call["messages"][1]["content"]
    assert "How long is data retained?" in user_prompt
    assert "Clause 1:\nProcessor acts on instructions." in user_prompt
    assert "Clause 2:\nData is kept for 30 days." in user_prompt
