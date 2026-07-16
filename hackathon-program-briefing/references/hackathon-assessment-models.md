# Hackathon assessment models

Use this reference when a hackathon / ML competition is also an academic practice, exam, or зачёт/незачёт gate.

## Core lesson

Do not assume the leaderboard should be the final result. For academic practice, the stated goal may be competent application of knowledge, not metric-maximization alone. A low score can still be a successful learning outcome when the code, pipeline, validation, and defense show real understanding. A high score can still be suspicious or insufficient when the team cannot explain the solution.

Design the assessment in two layers:

1. **Internal scenario matrix** — decide who should pass, need review, retake, or fail.
2. **Concise public regulation** — publish a short formula, tables, and audit clause.

Do not publish the whole scenario matrix unless the user wants an organizer/internal document. Participant-facing assessment should be terse and table-driven.

## Scenario-first design

Before locking a formula, design the assessment from scenarios:

```text
participant behavior -> evidence -> commission decision -> rubric implication
```

Core scenarios to distinguish:

| Scenario | Desired decision |
| --- | --- |
| Strong score + strong code + strong defense | Pass / high score |
| Weak or medium score + real ML work + strong technical defense | Pass possible |
| Weak score caused by a localized, understood bug | Pass or review depending on reproducibility and severity |
| Strong score + poor understanding of code/pipeline/model | Review or retake; score is not sufficient proof |
| Copied SOTA / AutoML / LLM-generated solution without understanding | Review; pass only if understanding is proven |
| Polished defense but code does not match the story | Do not award high defense score; review/retake |
| No valid submit but reproducible, meaningful work exists | Review; pass possible only if artifacts support the story |
| Non-reproducible code | Limit defense score; review or retake |
| Leakage, unauthorized data, plagiarism, or hidden manipulation | Suspend formula; commission/disqualification path |
| One team member understands everything and others do not | Decide whether grading is team-level or individual; otherwise review |

The point is to preserve the academic purpose: competent application of knowledge. Leaderboard is evidence; code, reproducibility, and defense decide what the evidence means.

## Concise public regulation pattern

Use this shape when the user wants a clean one-file assessment document.

```markdown
# Assessment Regulation

## Итоговая оценка

$$
\text{FinalScore} = 0.5 \cdot \text{LeaderboardScore} + 0.5 \cdot \text{DefenseScore}
$$

| Компонент | Вес | Шкала | Что оценивает |
| --- | ---: | ---: | --- |
| `LeaderboardScore` | 50% | 0–10 | Качество submit на leaderboard / private score |
| `DefenseScore` | 50% | 0–10 | Понимание решения, кода, pipeline, модели и результата |

## Условия зачёта

Зачёт ставится, если одновременно выполнены оба условия:

$$
\text{FinalScore} \ge 3.5
$$

$$
\text{DefenseScore} \ge 3.5
$$

Высокий leaderboard не компенсирует провальную защиту.
```

Use 50/50 when the user wants leaderboard and defense to be equally legible, but keep the **minimum defense threshold** so metric luck cannot replace understanding.

## Leaderboard conversion table

Prefer a table over prose:

| Результат на leaderboard / private score | `LeaderboardScore` |
| --- | ---: |
| Верхняя зона leaderboard | 8–10 |
| Уверенный рабочий результат | 6–7 |
| Средний результат | 4–5 |
| Слабый, но валидный submit | 1–3 |
| Нет валидного submit | 0 |

Add one sentence only: exact normalization is fixed after baseline, private score, and result distribution are known.

## Defense criteria table

Prefer a **process-first ML defense rubric** when the academic goal is to verify that participants correctly went through the ML lifecycle from data analysis to final submit. Do not make generic “code / presentation / submit consistency” one of the main educational criteria; keep that as an audit layer.

Recommended four equal criteria for HCK-ALFA-style ML practice:

| Критерий | Вес внутри `DefenseScore` | Описание |
| --- | ---: | --- |
| Глубина анализа данных | 25% | Оценивается понимание структуры датасета: целевой переменной, распределений, пропусков, выбросов, дисбаланса, типов признаков и различий между train/test. Участник должен объяснить, какие свойства данных повлияли на дальнейший pipeline и какие ограничения или риски были выявлены на этапе анализа. |
| Обоснованность feature engineering, использование выводов из данных | 25% | Оценивается, как выводы из анализа данных были использованы для создания, преобразования, отбора или исключения признаков. Участник должен обосновать preprocessing, работу с категориальными, числовыми и временными признаками, проверку leakage и влияние выбранных признаков на качество решения. |
| Корректность валидации и устойчивость к leaderboard-overfitting | 25% | Оценивается выбранная схема локальной валидации, её соответствие задаче, метрике и структуре данных. Участник должен показать, как сопоставлял локальные результаты с leaderboard, контролировал переобучение под public score и принимал решение о финальном submit. |
| Качество моделирования и обоснованность принятых решений | 25% | Оценивается выбор моделей, функций потерь, метрик, гиперпараметров и способов сравнения подходов. Участник должен объяснить, какие решения дали прирост качества, какие были отклонены и почему финальная конфигурация является обоснованной. |

Use the older generic criteria below only when the event is not specifically an ML-practice lifecycle defense, or as a checklist for interview questions rather than as the main scoring rubric:

| Критерий | Что проверяется |
| --- | --- |
| Анализ задачи, данных и признаков | Команда понимает постановку, признаки, ограничения датасета, возможные проблемы данных и почему выбранный подход уместен |
| Pipeline и воспроизводимость | Решение запускается от данных до submit; зависимости и шаги воспроизводимы |
| Модель и технические решения | Команда объясняет выбор модели, признаков, preprocessing и ключевых гипотез |
| Валидация и метрика | Команда понимает WMAE, validation setup, эксперименты и связь локальной проверки с leaderboard |
| Анализ ошибок и ограничений | Команда понимает, где модель ошибается, какие есть слабые места и что можно улучшить |
| Понимание кода | Команда может объяснить ключевые части notebook / pipeline |
| Соответствие артефактов | Защита, код и submit описывают одно и то же решение |

## Mining older rubrics

When Maxim remembers "we had criteria like depth of data analysis earlier", search session history and the vault for adjacent historical Alfa/OrangeHack rubrics before inventing new names. Useful query patterns:

- `"Банковское приложение будущего" "Анализ текущего пользовательского пути"`
- `"Трендвотчер" "Качество отбора" "Проверяемость источников"`
- `"Alpha Campus Start" "критерии"`
- `"критерии оценивания" "хакатон"`

Reusable historical rubrics found from Alpha Campus Start:

**Banking App / product case**

| Критерий | Вес | Reusable idea |
| --- | ---: | --- |
| Бизнес-значимость выбранного сценария | 15% | Start with why this scenario matters |
| Анализ текущего пользовательского пути | 25% | Reward depth of analysis before proposing a solution |
| Ценность предложенного решения | 25% | Check user/bank value, not just idea novelty |
| Реалистичность и приоритизация | 20% | Prefer focused MVP and explicit constraints |
| Качество прототипа и защиты | 15% | Artifact plus explanation quality |

**Trendwatcher / prototype case**

| Критерий | Вес | Reusable idea |
| --- | ---: | --- |
| Работоспособность прототипа | 35% | Show an end-to-end working path |
| Качество отбора и оценки сигналов | 25% | Reward signal selection and ranking logic |
| Полезность дайджеста / черновика | 20% | Assess usefulness of the output |
| Проверяемость источников и борьба с шумом | 10% | Require sources, duplicate/noise handling |
| Презентация и объяснение решения | 10% | Explanation and limitations |

For HCK-ALFA-style ML practice, do not copy these weights directly. Reuse the principle: evaluate depth of task/data analysis and reasoning before solution output, then adapt to ML-specific criteria.

## Audit / penalty clause

Keep the public clause short. Do not publish a long fraud taxonomy unless requested.

Recommended wording:

```markdown
## Дополнительная проверка

Любое решение может быть направлено на дополнительную проверку.

| Проверка | Что означает |
| --- | --- |
| Соответствие защиты, кода и submit | Рассказ должен подтверждаться артефактами |
| Воспроизводимость | Submit должен получаться из приложенного решения |
| Понимание pipeline | Команда отвечает за данные, признаки, модель и submit |
| Академическая добросовестность | Проверка на плагиат, leakage, запрещённые данные и непонятый AI-generated code |

При существенных нарушениях комиссия может снизить оценку, назначить дополнительную защиту / пересдачу или аннулировать результат.
```

Avoid words like “ложь” in regulations; use “существенные расхождения”, “недостоверное описание решения”, “невозможность подтвердить результат”, or “нарушение правил”.

## Obligatory artifacts table

| Артефакт | Требование |
| --- | --- |
| Submit | Загружен на платформу в заданном формате |
| Код решения | Позволяет получить финальный submit |
| Инструкция запуска | Описывает зависимости и порядок запуска |
| Описание подхода | Кратко объясняет данные, модель, валидацию и результат |
| Презентация / техническая карточка | Используется для защиты решения |

## Open questions to force before finalizing

- How to normalize private score / WMAE to a 0–10 `LeaderboardScore`?
- Is grading team-level only, or can individual participants receive different outcomes?
- Who handles disputes where formula passes but defense reveals non-understanding?
- What is the пересдача path for teams below threshold or with failed defense?
- Which checks are mandatory for all teams and which are audit-only?
