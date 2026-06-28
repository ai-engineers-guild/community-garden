BUILTIN_SKILLS: dict[str, str] = {
    "semantic_metrics/registry.yml": '''
metrics:
  belonging:
    title: "Belonging / чувство принадлежности"
    type: semantic
    scale: 0-100
    positive_signals:
      - repeated friendly interactions
      - people refer to shared memes or past discussions
      - newcomers receive warm responses
      - people return voluntarily
    negative_signals:
      - newcomers ignored
      - old-timers only talk to each other
      - public humiliation or dismissive tone
    required_evidence: [event_ids, thread_ids]
  safety:
    title: "Communication safety"
    type: semantic
    scale: 0-100
    positive_signals:
      - disagreement stays about ideas
      - people can ask simple questions
      - admins stop personal attacks
    negative_signals:
      - fear of asking basic questions
      - repeated personal attacks
      - sarcasm used to suppress participation
  self_sustainability:
    title: "Self-sustainability"
    type: mixed
    scale: 0-100
    positive_signals:
      - useful threads happen without admins
      - members answer newcomers
      - rituals continue without founder
    negative_signals:
      - every topic needs admin to start
      - no peer support
  rule_alignment:
    title: "Rule alignment"
    type: semantic
    scale: 0-100
    positive_signals:
      - members reinforce norms
      - rules match actual behavior
    negative_signals:
      - rules are ignored
      - admins violate rules they set
''',
    "role_analysis/roles.yml": '''
roles:
  steward:
    title: "Садовник"
    description: "Поддерживает нормы, помогает людям, снижает шум."
    positive_signals: [helps newcomers, summarizes, de-escalates, reinforces norms gently]
    negative_signals: [over-controls, polices too harshly]
  expert:
    title: "Эксперт"
    description: "Дает содержательные ответы по доменной теме."
    positive_signals: [detailed answers, examples, external references, practical advice]
    negative_signals: [condescension, ignores context]
  bridge:
    title: "Мост"
    description: "Соединяет группы, темы и людей."
    positive_signals: [mentions relevant people, connects topics, routes questions]
  bartender:
    title: "Бармен"
    description: "Создает third-place атмосферу."
    positive_signals: [soft humor, warmth, tension reduction]
    negative_signals: [derails useful threads]
  noise_generator:
    title: "Шумогенератор"
    description: "Много пишет, мало добавляет ценности."
    positive_signals: []
    negative_signals: [high volume, low replies, repeated derailment]
  risk_actor:
    title: "Поведенческий риск"
    description: "Повторяющийся паттерн вреда для среды. Не медицинский ярлык."
    negative_signals: [personal attacks, repeated emotional dumping, spam, norm erosion]
''',
    "risk_analysis/risk_taxonomy.yml": '''
risks:
  newcomer_churn_risk: "Newcomers ask or signal interest, but receive no meaningful response."
  expert_churn_risk: "Valuable expert contributions are ignored or punished."
  overload_risk: "Message volume makes the chat unreadable."
  tribal_capture_risk: "A subgroup captures agenda and suppresses others."
  emotional_dumping_risk: "A participant repeatedly uses the community as emotional discharge without reciprocal contribution."
  low_value_high_volume_risk: "Many messages, little value, frequent derailment."
  norm_erosion_risk: "Rules or implicit norms stop working."
  admin_dependency_risk: "Useful activity depends on one admin/founder."
''',
    "tribe_analysis/prompt.md": '''
# Tribe Analysis Skill

Input: graph metrics, actor packs, thread packs, recurring phrases, topics, conflicts.

Find candidate groups. For each group return: name, size estimate, core members, leaders, elders, symbols, rituals, values, conflicts, risks, opportunities, evidence ids, confidence.

Do not invent tribes without behavioral evidence.
''',
    "admin_mirror/prompt.md": '''
# Admin Mirror Skill

Analyze admin actions and omissions:
- where admins intervened on time;
- where they stayed silent;
- where they were too harsh;
- which experts they failed to amplify;
- whom they amplified incorrectly;
- which rules work;
- which rules should change.

Every finding must include evidence ids.
''',
    "recommendations/prompt.md": '''
# Recommendations Skill

Use metrics, findings, risks, tribe analysis, role analysis, admin mirror, and previous interventions.

Produce concrete actions with: priority, action, reason, evidence, owner, expected effect, success metric, risk.
''',
    "community-garden/SKILL.md": '''
# Community Garden Skill

Use this skill when analyzing community exports or maintaining recurring community reports.

Workflow:
1. Read `.garden/community.yml`.
2. Read `.garden/memory/*.md`.
3. Run `cg analyze --period <period>`.
4. Run `cg llm-pack weekly --period <period>`.
5. Use the LLM pack to run semantic skills.
6. Run `cg report weekly --period <period>`.
7. Update `.garden/interventions/queue.md`.

Rules:
- Do not invent evidence.
- Avoid psychiatric labels. Use behavioral risk language.
- Removal recommendations require repeated harm pattern and alternatives.
''',
}
