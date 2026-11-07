EXPLANATION_MAP = {
    "stress": "This verse reminds you that you do not have to carry everything on your own. God invites you to bring your burdens to Him and trust His care.",
    "healing": "This verse points to God's power to restore both body and heart. It reminds us that healing can come through His grace and timing.",
    "fear": "This verse reminds you that God is present with you even in uncertain moments. His strength is greater than anything you are facing.",
    "anger": "This verse encourages you to pause and respond with wisdom instead of reacting quickly. It reminds you that self-control reflects strength, not weakness.",
    "hope": "This verse points you toward God's promises for your future. Even when things feel uncertain, hope is found in trusting Him.",
    "love": "This verse reveals the depth of God's love and calls you to reflect that love to others. It reminds you that love is a choice expressed through action.",
    "anxiety": "This verse reminds you to bring your worries to God instead of letting them control you. His peace is available even in overwhelming moments.",
    "doubt": "This verse encourages you to hold on to faith even when you have questions. God is not distant in your doubts, but present within them.",
    "work": "This verse reminds you that your work has purpose beyond results. Doing your best with integrity is a way of honoring God.",
    "temptation": "This verse reminds you that you are not alone in your struggles. God provides strength and a way forward when you feel tested.",
    "joy": "This verse reminds you that joy is not based only on circumstances. It comes from staying connected to God even in changing situations.",
}

CHALLENGE_MAP = {
    "stress": "Take 5 quiet minutes today to read this verse again and pray about one thing weighing on you.",
    "healing": "Pray for someone who is hurting today and send them an encouraging message.",
    "fear": "Read this passage slowly today and write down one way God has been faithful to you before.",
    "anger": "Before reacting to anything today, pause, take three slow breaths, and say a short prayer.",
    "hope": "Write down one promise of God and put it somewhere you will see it this week.",
    "love": "Do one unexpected kind thing for someone today without telling anyone.",
    "anxiety": "Each time you feel worried today, stop and pray one sentence to God about it.",
    "doubt": "Write down one honest question you have about faith and bring it to a youth leader this week.",
    "work": "Do one task today with extra care, as if you were doing it for God.",
    "temptation": "Memorize this verse today and repeat it when you feel tested.",
    "joy": "Write down three things you are thankful for and share one with a friend.",
}

REFLECTION_MAP = {
    "stress": "What is one thing you need to release to God today?",
    "healing": "Where in your life do you need healing right now?",
    "fear": "What would it look like to trust God in the area you feel afraid?",
    "anger": "What situation today requires a calmer and wiser response from you?",
    "hope": "What promise of God can you hold onto today?",
    "love": "Who can you intentionally show love to today?",
    "anxiety": "What worry are you holding onto instead of giving to God?",
    "doubt": "What question or uncertainty can you bring honestly to God today?",
    "work": "How can you approach your work today with greater purpose?",
    "temptation": "What is one area where you need to choose discipline over comfort?",
    "joy": "What is one thing you can thank God for today?",
}


def generate_fallback_content(topic: str, reference: str):
    topic_key = topic.lower().strip()

    return {
        "explanation": EXPLANATION_MAP.get(
            topic_key,
            "This verse offers encouragement and points you back to God's faithfulness.",
        ),
        "challenge": CHALLENGE_MAP.get(
            topic_key,
            f"Read the passage around {reference} today and share one thing you learned with a friend.",
        ),
        "reflection_question": REFLECTION_MAP.get(
            topic_key,
            f"What is God showing you through {reference} today?",
        ),
    }