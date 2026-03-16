def generate_fallback_content(topic: str, reference: str):
    topic_lower = topic.lower()

    explanation_map = {
        "stress": "This verse reminds you to bring your worries to God instead of carrying them alone. God cares about what is weighing on your heart.",
        "fear": "This verse is a reminder that God is with you and strengthens you. You do not have to face life feeling alone.",
        "purpose": "This verse points to God's direction and intention for your life. Even when you do not see the full path yet, God is still leading.",
        "work": "This verse encourages you to work with sincerity and faithfulness. Your effort can still honor God even in ordinary tasks.",
        "wisdom": "This verse reminds you that God gives wisdom to those who ask. You can come to Him honestly when you need direction.",
        "peace": "This verse points you toward the peace God gives, even in difficult moments. His peace is deeper than changing circumstances.",
        "healing": "We are healed by the power of Jesus"
    }

    prayer_map = {
        "stress": "Lord, help me bring my worries to You today. Give me peace and teach me to trust You.",
        "fear": "Lord, when I feel afraid, remind me that You are with me. Strengthen my heart and guide me.",
        "purpose": "Lord, help me trust Your plan for my life. Lead me clearly and help me walk faithfully.",
        "work": "Lord, help me serve with excellence and integrity. Let my work reflect Your character.",
        "wisdom": "Lord, give me wisdom for the decisions before me. Help me recognize Your direction.",
        "peace": "Lord, calm my heart and fill me with Your peace. Help me rest in Your presence.",
        "healing": "Lord, please heal me both physically and also heal my heart"
    }

    reflection_map = {
        "stress": "What worry do you need to hand over to God today?",
        "fear": "Where do you need to trust God more deeply right now?",
        "purpose": "What step of obedience might God be asking of you today?",
        "work": "How can you honor God in your work or studies this week?",
        "wisdom": "What decision do you need God's wisdom for right now?",
        "peace": "What would it look like to slow down and receive God's peace today?",
        "healing": "What or who would you like God to heal and do you belive He will?"
    }

    explanation = explanation_map.get(
        topic_lower,
        "This verse offers encouragement and points you back to God's faithfulness."
    )

    prayer = prayer_map.get(
        topic_lower,
        "Lord, help me receive the truth of this verse and live by it today."
    )

    reflection_question = reflection_map.get(
        topic_lower,
        f"What is God showing you through {reference} today?"
    )

    return {
        "explanation": explanation,
        "prayer": prayer,
        "reflection_question": reflection_question
    }