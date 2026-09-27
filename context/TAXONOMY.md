# Technical Skill Taxonomy & Role Affinities

## 🌐 Overview

CareerLens AI utilizes a deterministic, symbol-aware database of **450+ canonical IT engineering skills** categorized into **14 engineering domains**, coupled with **17 IT engineering role profiles** for candidate role affinity scoring.

---

## 🗂️ 14 IT Engineering Domains

1. **`languages`**: Core programming and scripting languages (e.g. Python, TypeScript, JavaScript, Java, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala).
2. **`frontend`**: Web UI libraries, frameworks, and state management (e.g. React, Next.js, Vue.js, Angular, Svelte, Tailwind CSS, Redux, Zustand, HTML5, CSS3).
3. **`backend`**: Server-side frameworks and runtimes (e.g. FastAPI, Node.js, Express, Django, Flask, Spring Boot, ASP.NET Core, Ruby on Rails, NestJS, Gin).
4. **`databases`**: Relational, NoSQL, and vector storage engines (e.g. PostgreSQL, MySQL, MongoDB, Redis, SQLite, Cassandra, DynamoDB, Elasticsearch, Supabase, ClickHouse).
5. **`cloud_devops`**: Cloud infrastructure, containers, and CI/CD pipelines (e.g. AWS, Azure, Google Cloud, Docker, Kubernetes, Terraform, GitHub Actions, GitLab CI, CI/CD).
6. **`ai_ml_data_science`**: Machine learning frameworks and data analysis (e.g. PyTorch, TensorFlow, Scikit-Learn, Pandas, NumPy, Keras, OpenCV, Hugging Face).
7. **`genai_llms`**: Generative AI, Large Language Models, and RAG frameworks (e.g. LangChain, LlamaIndex, RAG Pipelines, Vector Databases, Fine-Tuning, Ollama, Prompt Engineering).
8. **`big_data`**: Distributed data streaming and batch processing (e.g. Apache Spark, Apache Kafka, Apache Flink, Apache Airflow, Snowflake, Databricks, Hadoop).
9. **`mobile`**: Cross-platform and native mobile app development (e.g. React Native, Flutter, Android SDK, iOS SDK, Swift, Kotlin).
10. **`testing_qa`**: Testing frameworks, automation, and QA (e.g. PyTest, Jest, Cypress, Playwright, Selenium, JUnit, Postman).
11. **`security`**: Application and cloud cybersecurity (e.g. OAuth2, JWT, OWASP, Penetration Testing, IAM, SOC2, Cryptography).
12. **`system_design`**: Architectural patterns and distributed systems (e.g. Microservices, REST APIs, GraphQL, gRPC, Event-Driven Architecture, WebSockets).
13. **`embedded_iot`**: Low-level systems and hardware engineering (e.g. RTOS, FreeRTOS, Arduino, Raspberry Pi, ARM, I2C, SPI, UART).
14. **`tools_collaboration`**: Developer tooling, version control, and methodologies (e.g. Git, GitHub, GitLab, Jira, Agile, Scrum, Confluence).

---

## ⚡ Symbol-Aware Boundary Matching

Standard word boundaries (`\b`) fail on technical terms containing punctuation or symbols (e.g., `\bC++\b` does not match because `+` is not a word character).

CareerLens AI utilizes custom pre-compiled regex matchers:

| Skill            | Challenge                           | Matching Pattern                                                            |
| ---------------- | ----------------------------------- | --------------------------------------------------------------------------- |
| **C++**          | `+` breaks `\b`                     | `(?:\b\|(?<=\s))C\+\+(?=[,\s\.\/\)]\|$)`                                    |
| **C#**           | `#` breaks `\b`                     | `(?:\b\|(?<=\s))C#(?=[,\s\.\/\)]\|$)`                                       |
| **ASP.NET Core** | Leading dot `.` and optional `Core` | `(?:\b\|(?<=\s))\.(NET\|net)(?:\s+(?:Core\|core))?(?=[,\s\.\/\)]\|$)`       |
| **CI/CD**        | Forward slash `/`                   | `(?:\b\|(?<=\s))CI\/CD(?=[,\s\.\/\)]\|$)`                                   |
| **C**            | Single character false positives    | `(?:\b\|(?<=\s))C(?=[,\s\.\/\)]+(?:programming\|language\|code))\b`         |
| **Go**           | Common English verb                 | `(?:\b\|(?<=\s))(?:Go\|Golang)(?=[,\s\.\/\)]+(?:programming\|developer))\b` |

---

## 🎯 Role Affinity Scoring Formula

Candidate role affinities are calculated across 17 target profiles (such as _AI/ML Engineer_, _Full Stack Engineer_, _Cloud & DevOps Engineer_, _Frontend Engineer_, etc.).

Each role profile defines **Core Skills** (weighted 2.5) and **Secondary Skills** (weighted 1.0):

$$\text{Affinity \%} = \min\left(100.0, \; \frac{2.5 \cdot |\text{Matched Core}| + 1.0 \cdot |\text{Matched Secondary}|}{2.5 \cdot |\text{Total Core}| + 1.0 \cdot |\text{Total Secondary}|} \times 160.0\right)$$

The top 3 role affinities are returned with the candidate profile as recommendations and career alignment insights.
