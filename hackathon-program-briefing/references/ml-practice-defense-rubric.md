# ML practice defense rubric

Use this when Maxim designs criteria for an ML hackathon-practice, coursework-like ML defense, or academic competition where the goal is to verify the participant's full process, not just presentation quality or code/submit consistency.

## Preferred rubric shape

Keep the main educational rubric process-first and factual. Do not make code-submit-defense consistency a primary criterion; keep it in a separate audit/check layer together with reproducibility, plagiarism, leakage, forbidden data, and artifact validity.

Recommended four equal criteria:

1. **Глубина анализа данных** — 25%  
   Оценивается понимание структуры датасета: целевой переменной, распределений, пропусков, выбросов, дисбаланса, типов признаков и различий между train/test. Участник должен объяснить, какие свойства данных повлияли на дальнейший pipeline и какие ограничения или риски были выявлены на этапе анализа.

2. **Обоснованность feature engineering, использование выводов из данных** — 25%  
   Оценивается, как выводы из анализа данных были использованы для создания, преобразования, отбора или исключения признаков. Участник должен обосновать preprocessing, работу с категориальными, числовыми и временными признаками, проверку leakage и влияние выбранных признаков на качество решения.

3. **Корректность валидации и устойчивость к leaderboard-overfitting** — 25%  
   Оценивается выбранная схема локальной валидации, её соответствие задаче, метрике и структуре данных. Участник должен показать, как сопоставлял локальные результаты с leaderboard, контролировал переобучение под public score и принимал решение о финальном submit.

4. **Качество моделирования и обоснованность принятых решений** — 25%  
   Оценивается выбор моделей, функций потерь, метрик, гиперпараметров и способов сравнения подходов. Участник должен объяснить, какие решения дали прирост качества, какие были отклонены и почему финальная конфигурация является обоснованной.

## Style constraints

- Use concise, rubric-ready wording.
- Prefer facts and observable evidence over abstract qualities.
- Avoid weak criteria like “quality of presentation” unless the user explicitly wants presentation scoring.
- Baseline can be mentioned only if useful; Maxim does not want baseline as a standalone criterion for this rubric class.
- Keep descriptions to about two factual sentences per criterion when drafting a public regulation.
