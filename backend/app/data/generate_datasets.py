import json
import random

# 1. EXPANDED SKILL TAXONOMY
taxonomy = {
    "Programming Languages": {
        "Python": ["python", "python3", "py", "cpython"],
        "Java": ["java", "core java", "java8", "java 11", "j2ee"],
        "C++": ["c++", "cpp", "modern c++"],
        "C": ["c programming", "c language"],
        "C#": ["c#", "csharp", ".net", "dotnet"],
        "JavaScript": ["javascript", "js", "es6", "vanilla js"],
        "TypeScript": ["typescript", "ts"],
        "Go": ["golang", "go language"],
        "Rust": ["rust", "rustlang"],
        "R": ["r language", "r programming", "rstudio"],
        "SQL": ["sql", "structured query language", "ansi sql", "plsql", "t-sql"],
        "Scala": ["scala"],
        "Bash": ["bash", "shell scripting", "shell", "sh", "zsh"]
    },
    "Data Science & Analytics": {
        "Pandas": ["pandas", "pd"],
        "NumPy": ["numpy", "np"],
        "SciPy": ["scipy"],
        "Exploratory Data Analysis": ["eda", "exploratory data analysis", "data exploration", "data inspection"],
        "Data Cleaning": ["data cleaning", "data wrangling", "data preprocessing", "data imputation"],
        "Statistics": ["statistics", "statistical analysis", "probability", "hypothesis testing", "inferential statistics", "statistical modeling"],
        "Matplotlib": ["matplotlib", "pyplot"],
        "Seaborn": ["seaborn", "sns"],
        "Plotly": ["plotly", "cufflinks", "interactive charts"],
        "Tableau": ["tableau", "tableau desktop"],
        "Power BI": ["power bi", "powerbi", "dax", "power query"],
        "Excel": ["excel", "advanced excel", "vlookup", "pivot tables", "excel formulas"],
        "A/B Testing": ["a/b testing", "ab testing", "experimentation", "split testing"]
    },
    "Machine Learning": {
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "Supervised Learning": ["supervised learning", "regression", "classification", "linear regression", "logistic regression"],
        "Unsupervised Learning": ["unsupervised learning", "clustering", "k-means", "hierarchical clustering", "dbscan"],
        "Random Forest": ["random forest", "decision trees", "extra trees"],
        "XGBoost": ["xgboost", "gradient boosting", "lightgbm", "catboost", "gbm"],
        "Feature Engineering": ["feature engineering", "feature selection", "dimensionality reduction", "pca", "t-sne"],
        "Model Evaluation": ["model evaluation", "cross-validation", "roc-auc", "precision-recall", "f1-score", "hyperparameter tuning"],
        "Recommender Systems": ["recommender systems", "recommendation systems", "collaborative filtering", "content-based filtering"],
        "Time Series Analysis": ["time series", "arima", "prophet", "forecasting", "sarima"],
        "Explainable AI": ["explainable ai", "xai", "shap", "lime", "feature attribution"]
    },
    "Deep Learning & AI": {
        "PyTorch": ["pytorch", "torch", "torchvision"],
        "TensorFlow": ["tensorflow", "tf", "tf.keras"],
        "Keras": ["keras"],
        "Neural Networks": ["neural networks", "ann", "deep learning", "multilayer perceptron"],
        "Convolutional Neural Networks": ["cnn", "convolutional neural networks", "computer vision", "opencv", "object detection", "yolo"],
        "Recurrent Neural Networks": ["rnn", "lstm", "gru"],
        "Transformers": ["transformers", "attention mechanism", "hugging face", "huggingface", "bert", "roberta"],
        "Natural Language Processing": ["nlp", "natural language processing", "spacy", "nltk", "text processing", "tokenization", "lemmatization"],
        "Large Language Models": ["llm", "llms", "large language models", "langchain", "rag", "retrieval-augmented generation", "prompt engineering", "llamaindex"],
        "Vector Databases": ["vector search", "faiss", "chromadb", "pinecone", "milvus", "qdrant"]
    },
    "MLOps & Big Data": {
        "Apache Spark": ["spark", "pyspark", "apache spark", "spark streaming"],
        "Apache Kafka": ["kafka", "apache kafka", "event streaming", "message broker"],
        "Hadoop": ["hadoop", "hdfs", "mapreduce"],
        "MLflow": ["mlflow", "experiment tracking", "model registry"],
        "Airflow": ["airflow", "apache airflow", "workflow orchestration", "etl pipelines"],
        "Docker": ["docker", "containerization", "docker compose", "containers", "dockerfile"],
        "Kubernetes": ["kubernetes", "k8s", "container orchestration"],
        "Model Deployment": ["model deployment", "model serving", "triton", "torchserve", "onnx", "fastapi serving"]
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services", "s3", "ec2", "lambda", "sagemaker", "cloudwatch"],
        "Google Cloud": ["gcp", "google cloud", "bigquery", "vertex ai", "cloud storage"],
        "Azure": ["azure", "microsoft azure", "azure ml", "azure devops"],
        "CI/CD": ["ci/cd", "continuous integration", "github actions", "jenkins", "gitlab ci"],
        "Git": ["git", "github", "version control", "gitlab", "bitbucket"],
        "Linux": ["linux", "unix", "ubuntu", "centos", "terminal", "bash"]
    },
    "Web & Software Engineering": {
        "FastAPI": ["fastapi", "asgi"],
        "Flask": ["flask", "wsgi"],
        "Django": ["django", "django rest framework", "drf"],
        "React": ["react", "react.js", "reactjs", "react native"],
        "Node.js": ["node", "node.js", "nodejs"],
        "Express": ["express", "express.js"],
        "REST APIs": ["rest api", "restful apis", "rest", "api development", "json api", "endpoint"],
        "GraphQL": ["graphql", "apollo"],
        "HTML/CSS": ["html", "html5", "css", "css3", "tailwind", "bootstrap", "sass"],
        "Data Structures & Algorithms": ["dsa", "data structures", "algorithms", "competitive programming", "leetcode", "problem solving"],
        "System Design": ["system design", "microservices", "software architecture", "scalability", "load balancing"]
    },
    "Database Systems": {
        "PostgreSQL": ["postgresql", "postgres", "psql"],
        "MySQL": ["mysql", "mariadb"],
        "MongoDB": ["mongodb", "nosql", "mongo", "document db"],
        "Redis": ["redis", "caching", "in-memory database"],
        "Elasticsearch": ["elasticsearch", "elk stack", "opensearch"]
    }
}

with open("backend/app/data/skill_taxonomy.json", "w") as f:
    json.dump(taxonomy, f, indent=2)

# 2. CURATED REAL-WORLD JOBS DATASET (120 Jobs across 8 career families)
roles_templates = [
    {
        "role": "Data Scientist",
        "category": "Data Science",
        "req": ["Python", "SQL", "Machine Learning", "Pandas", "Scikit-Learn", "Statistics"],
        "pref": ["Deep Learning", "PyTorch", "AWS", "Docker", "Explainable AI"],
        "min_exp": 1,
        "sal_range": "₹8,00,000 - ₹18,00,000",
        "desc_template": "Looking for a Data Scientist to analyze complex datasets, build predictive machine learning models, and derive actionable business intelligence. You will conduct exploratory data analysis, feature engineering, and deploy models using Python and Scikit-Learn."
    },
    {
        "role": "Machine Learning Engineer",
        "category": "Artificial Intelligence",
        "req": ["Python", "Machine Learning", "PyTorch", "Docker", "Scikit-Learn", "FastAPI"],
        "pref": ["MLOps", "Kubernetes", "AWS", "MLflow", "Transformers"],
        "min_exp": 2,
        "sal_range": "₹10,00,000 - ₹24,00,000",
        "desc_template": "Seeking an ML Engineer to take prototypes to production. You will design, train, evaluate, and deploy scalable ML and Deep Learning architectures with PyTorch and containerize microservices using Docker and Kubernetes."
    },
    {
        "role": "Data Analyst",
        "category": "Data Analytics",
        "req": ["SQL", "Excel", "Power BI", "Tableau", "Data Cleaning", "Statistics"],
        "pref": ["Python", "Pandas", "A/B Testing"],
        "min_exp": 0,
        "sal_range": "₹5,00,000 - ₹11,00,000",
        "desc_template": "Join our team as a Data Analyst to transform raw enterprise data into meaningful dashboards and reports. Must be proficient in advanced SQL queries, Power BI or Tableau visualization, and statistical reporting."
    },
    {
        "role": "AI Research Engineer",
        "category": "Artificial Intelligence",
        "req": ["Python", "PyTorch", "Transformers", "Natural Language Processing", "Deep Learning"],
        "pref": ["Large Language Models", "Vector Databases", "Git", "Hugging Face"],
        "min_exp": 2,
        "sal_range": "₹14,00,000 - ₹30,00,000",
        "desc_template": "We are seeking an AI Research Engineer to experiment with cutting-edge Transformer architectures, fine-tune LLMs, and develop RAG pipelines for semantic search and generative intelligence."
    },
    {
        "role": "MLOps Engineer",
        "category": "DevOps & Big Data",
        "req": ["Python", "Docker", "Kubernetes", "CI/CD", "AWS", "MLflow"],
        "pref": ["Airflow", "Linux", "Git", "Model Deployment"],
        "min_exp": 2,
        "sal_range": "₹12,00,000 - ₹26,00,000",
        "desc_template": "Responsible for automating continuous integration and deployment pipelines for ML models, tracking experiments using MLflow, and orchestrating container workloads on AWS Kubernetes clusters."
    },
    {
        "role": "Full Stack Developer",
        "category": "Software Engineering",
        "req": ["JavaScript", "React", "Node.js", "REST APIs", "HTML/CSS", "MongoDB"],
        "pref": ["TypeScript", "Docker", "PostgreSQL", "Git"],
        "min_exp": 1,
        "sal_range": "₹6,00,000 - ₹16,00,000",
        "desc_template": "Looking for a Full Stack Developer to build high-performance web applications using React on the frontend and Node.js / Express on the backend, connecting with MongoDB and relational databases."
    },
    {
        "role": "Backend Engineer (Python)",
        "category": "Software Engineering",
        "req": ["Python", "FastAPI", "PostgreSQL", "REST APIs", "Docker", "Git"],
        "pref": ["Redis", "Linux", "CI/CD", "System Design"],
        "min_exp": 1,
        "sal_range": "₹7,00,000 - ₹18,00,000",
        "desc_template": "Develop robust, scalable backend microservices using FastAPI, optimize database queries on PostgreSQL, build Redis caching layers, and deploy services via Docker."
    },
    {
        "role": "Big Data Engineer",
        "category": "DevOps & Big Data",
        "req": ["Python", "SQL", "Apache Spark", "Airflow", "Hadoop"],
        "pref": ["Apache Kafka", "AWS", "Scala", "PostgreSQL"],
        "min_exp": 2,
        "sal_range": "₹9,00,000 - ₹20,00,000",
        "desc_template": "Architect and manage large-scale distributed data processing pipelines using PySpark, orchestrate batch workflows with Apache Airflow, and stream real-time events with Kafka."
    }
]

companies = [
    "Google", "Microsoft", "Amazon", "Flipkart", "Swiggy", "Zomato", "Jio", "CRED",
    "Razorpay", "Infosys", "TCS", "Wipro", "Accenture", "Deloitte", "Fractal Analytics",
    "Mu Sigma", "Tiger Analytics", "PhonePe", "InMobi", "Paytm", "Oracle", "Cisco",
    "Intel", "NVIDIA", "Adobe", "Salesforce", "Uber", "Ola", "Meesho", "BrowserStack"
]

locations = ["Bengaluru, India", "Hyderabad, India", "Pune, India", "Mumbai, India", "Delhi NCR, India", "Remote"]

jobs_list = []
job_id = 1

for role_meta in roles_templates:
    # Generate 15 jobs per role (120 total)
    for i in range(15):
        comp = random.choice(companies)
        loc = random.choice(locations)
        title_prefix = random.choice(["Associate", "Junior", "", "Senior", "Lead"]) if i > 3 else ""
        job_title = f"{title_prefix} {role_meta['role']}".strip()
        
        # slight variance in skills
        req_skills = list(role_meta["req"])
        pref_skills = list(role_meta["pref"])
        if i % 3 == 0 and len(pref_skills) > 0:
            swapped = pref_skills.pop(0)
            req_skills.append(swapped)
        
        desc = f"{role_meta['desc_template']} As a member of our team at {comp} ({loc}), you will collaborate with cross-functional engineers to drive business value. Key technologies: {', '.join(req_skills[:4])}."
        
        jobs_list.append({
            "id": f"job-{job_id:03d}",
            "title": job_title,
            "role": role_meta["role"],
            "category": role_meta["category"],
            "company": comp,
            "location": loc,
            "min_experience_years": max(0, role_meta["min_exp"] + (1 if "Senior" in job_title else (0 if "" in job_title else -1))),
            "education": "B.Tech / B.E. / M.Sc / MCA in Computer Science, Data Science or related field",
            "salary_range": role_meta["sal_range"],
            "required_skills": req_skills,
            "preferred_skills": pref_skills,
            "description": desc
        })
        job_id += 1

with open("backend/app/data/jobs_dataset.json", "w") as f:
    json.dump(jobs_list, f, indent=2)

# 3. PERSONALIZED LEARNING ROADMAP RESOURCES
learning_resources = {
    "Docker": {
        "prerequisites": ["Linux", "Git"],
        "difficulty": "Intermediate",
        "estimated_hours": 18,
        "summary": "Containerize machine learning microservices and web backends for reproducible deployments.",
        "milestones": [
            "Understand Images vs Containers, namespaces and cgroups",
            "Write multi-stage Dockerfiles for Python & FastAPI applications",
            "Compose multi-service setups with Docker Compose (App + Database + Redis)"
        ],
        "free_tutorials": [
            {"title": "Docker for Beginners (Docker Official)", "url": "https://docs.docker.com/get-started/"},
            {"title": "Docker in 100 Seconds & Full Course (Fireship / freeCodeCamp)", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"}
        ],
        "project_idea": "Build and containerize a FastAPI ML inference service with a health-check endpoint and deploy locally via docker-compose."
    },
    "AWS": {
        "prerequisites": ["Linux", "Docker"],
        "difficulty": "Intermediate",
        "estimated_hours": 24,
        "summary": "Deploy cloud-native scalable ML workloads, object storage (S3), and serverless functions (Lambda).",
        "milestones": [
            "Setup AWS IAM roles, CLI and security policies",
            "Deploy ML pipelines on Amazon EC2 and S3 object buckets",
            "Explore AWS SageMaker endpoints and AWS Lambda serverless triggers"
        ],
        "free_tutorials": [
            {"title": "AWS Cloud Practitioner Essentials (AWS Skill Builder)", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"},
            {"title": "Deploying Machine Learning on AWS (Coursera / YouTube)", "url": "https://aws.amazon.com/getting-started/hands-on/"}
        ],
        "project_idea": "Deploy a sentiment analysis model on AWS EC2 behind an NGINX reverse proxy with automated S3 dataset backups."
    },
    "Kubernetes": {
        "prerequisites": ["Docker", "Linux"],
        "difficulty": "Advanced",
        "estimated_hours": 30,
        "summary": "Orchestrate containerized services with auto-scaling, load balancing, and self-healing deployments.",
        "milestones": [
            "Master Pods, Deployments, ReplicaSets, and Services",
            "Configure Ingress controllers and ConfigMaps/Secrets",
            "Deploy ML serving models with horizontal pod autoscalers (HPA)"
        ],
        "free_tutorials": [
            {"title": "Kubernetes Official Tutorials (Interactive Minikube)", "url": "https://kubernetes.io/docs/tutorials/"},
            {"title": "Kubernetes Course for Beginners (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=X48VuDVv0do"}
        ],
        "project_idea": "Spin up a local Minikube cluster and deploy a scaled 3-replica REST API model server with ingress routing."
    },
    "PyTorch": {
        "prerequisites": ["Python", "NumPy", "Linear Algebra"],
        "difficulty": "Intermediate",
        "estimated_hours": 35,
        "summary": "Build, train, and fine-tune deep neural networks and transformer architectures using dynamic computation graphs.",
        "milestones": [
            "Tensors, Autograd, and GPU acceleration with CUDA",
            "Custom nn.Module architectures, Loss functions, and Optimizers",
            "Training loops, DataLoader, validation, and saving checkpoints"
        ],
        "free_tutorials": [
            {"title": "Deep Learning with PyTorch: A 60 Minute Blitz", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html"},
            {"title": "PyTorch for Deep Learning Bootcamp (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=V_xro1bcAuA"}
        ],
        "project_idea": "Implement a ResNet image classifier or an LSTM time-series predictor in PyTorch with TensorBoard monitoring."
    },
    "Transformers": {
        "prerequisites": ["PyTorch", "Natural Language Processing"],
        "difficulty": "Advanced",
        "estimated_hours": 30,
        "summary": "Fine-tune modern Transformer models (BERT, RoBERTa, T5) and build semantic retrieval search engines.",
        "milestones": [
            "Self-attention mathematics, Positional encodings, and Multi-head attention",
            "Hugging Face transformers pipeline, tokenizers, and datasets",
            "Semantic embeddings and dense passage retrieval with Sentence Transformers"
        ],
        "free_tutorials": [
            {"title": "Hugging Face NLP Course (Official)", "url": "https://huggingface.co/learn/nlp-course/chapter1/1"},
            {"title": "Sentence Transformers Documentation & Guides", "url": "https://www.sbert.net/"}
        ],
        "project_idea": "Build a semantic resume-job search engine matching candidate profiles with dense embeddings."
    },
    "Power BI": {
        "prerequisites": ["Excel", "SQL"],
        "difficulty": "Beginner",
        "estimated_hours": 15,
        "summary": "Create executive visual analytics dashboards, calculate DAX measures, and model business data.",
        "milestones": [
            "Data ingestion and transformation via Power Query",
            "Star schema dimensional data modeling and relationships",
            "DAX measures (CALCULATE, SUMX, RELATED) and interactive cross-filtering"
        ],
        "free_tutorials": [
            {"title": "Microsoft Power BI Guided Learning", "url": "https://learn.microsoft.com/en-us/power-bi/guided-learning/"},
            {"title": "Power BI Full Course (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=TmhQCQr_8DQ"}
        ],
        "project_idea": "Design an interactive HR Recruitment Dashboard analyzing hiring funnel metrics and time-to-hire across departments."
    },
    "MLOps": {
        "prerequisites": ["Python", "Docker", "Machine Learning"],
        "difficulty": "Advanced",
        "estimated_hours": 28,
        "summary": "Manage end-to-end machine learning lifecycles: experiment tracking, data versioning, and continuous model monitoring.",
        "milestones": [
            "Experiment logging and model registry with MLflow",
            "Data & model artifact version control with DVC",
            "Automated training and evaluation CI/CD pipelines"
        ],
        "free_tutorials": [
            {"title": "Made With ML (Goku Mohandas MLOps Course)", "url": "https://madewithml.com/"},
            {"title": "Full Stack Deep Learning MLOps", "url": "https://fullstackdeeplearning.com/"}
        ],
        "project_idea": "Build an automated MLflow pipeline that triggers retraining on new data batches and logs model validation metrics."
    },
    "PostgreSQL": {
        "prerequisites": ["SQL"],
        "difficulty": "Intermediate",
        "estimated_hours": 16,
        "summary": "Master relational database schema design, indexing, window functions, and query optimization.",
        "milestones": [
            "Advanced SQL: CTEs, Window functions (ROW_NUMBER, RANK, LAG/LEAD)",
            "Database normalization, Foreign keys, and Index types (B-Tree, GIN, GiST)",
            "Query execution plans with EXPLAIN ANALYZE and transaction isolation levels"
        ],
        "free_tutorials": [
            {"title": "PostgreSQL Tutorial for Beginners", "url": "https://www.postgresqltutorial.com/"},
            {"title": "Advanced SQL & Database Design (freeCodeCamp)", "url": "https://www.youtube.com/watch?v=HXV3zeRR3h4"}
        ],
        "project_idea": "Design a relational schema for an e-commerce platform with partitioned order tables and optimized indexing."
    }
}

with open("backend/app/data/learning_resources.json", "w") as f:
    json.dump(learning_resources, f, indent=2)

# 4. MARKET TRENDS DATASET FOR ANALYTICS DASHBOARD
market_trends = {
    "top_demanded_skills": [
        {"skill": "Python", "demand_percentage": 88, "growth_yoy": "+18%", "domain": "Data Science & AI"},
        {"skill": "SQL", "demand_percentage": 76, "growth_yoy": "+12%", "domain": "Data & Databases"},
        {"skill": "Machine Learning", "demand_percentage": 72, "growth_yoy": "+24%", "domain": "AI"},
        {"skill": "Docker", "demand_percentage": 65, "growth_yoy": "+31%", "domain": "DevOps & Cloud"},
        {"skill": "AWS", "demand_percentage": 61, "growth_yoy": "+20%", "domain": "Cloud"},
        {"skill": "PyTorch", "demand_percentage": 54, "growth_yoy": "+45%", "domain": "Deep Learning"},
        {"skill": "FastAPI", "demand_percentage": 49, "growth_yoy": "+38%", "domain": "Backend"},
        {"skill": "Power BI", "demand_percentage": 46, "growth_yoy": "+15%", "domain": "Analytics"},
        {"skill": "Kubernetes", "demand_percentage": 42, "growth_yoy": "+28%", "domain": "DevOps"},
        {"skill": "Transformers", "demand_percentage": 39, "growth_yoy": "+65%", "domain": "GenAI"}
    ],
    "salary_by_role": [
        {"role": "AI Research Engineer", "entry_level_lpa": 12.5, "mid_level_lpa": 22.0, "senior_level_lpa": 38.0},
        {"role": "Machine Learning Engineer", "entry_level_lpa": 9.5, "mid_level_lpa": 18.5, "senior_level_lpa": 32.0},
        {"role": "Data Scientist", "entry_level_lpa": 8.0, "mid_level_lpa": 16.0, "senior_level_lpa": 28.0},
        {"role": "MLOps Engineer", "entry_level_lpa": 10.0, "mid_level_lpa": 19.0, "senior_level_lpa": 30.0},
        {"role": "Data Analyst", "entry_level_lpa": 5.0, "mid_level_lpa": 9.5, "senior_level_lpa": 15.0},
        {"role": "Backend Engineer", "entry_level_lpa": 6.5, "mid_level_lpa": 14.0, "senior_level_lpa": 25.0},
        {"role": "Full Stack Developer", "entry_level_lpa": 6.0, "mid_level_lpa": 13.5, "senior_level_lpa": 24.0},
        {"role": "Big Data Engineer", "entry_level_lpa": 8.5, "mid_level_lpa": 16.5, "senior_level_lpa": 27.0}
    ],
    "role_skill_overlap": [
        {"role": "Data Scientist", "ml_overlap": 92, "devops_overlap": 45, "backend_overlap": 60, "analytics_overlap": 88},
        {"role": "ML Engineer", "ml_overlap": 95, "devops_overlap": 78, "backend_overlap": 82, "analytics_overlap": 65},
        {"role": "Data Analyst", "ml_overlap": 40, "devops_overlap": 20, "backend_overlap": 30, "analytics_overlap": 95},
        {"role": "AI Research Engineer", "ml_overlap": 98, "devops_overlap": 55, "backend_overlap": 50, "analytics_overlap": 60},
        {"role": "Full Stack Dev", "ml_overlap": 25, "devops_overlap": 60, "backend_overlap": 95, "analytics_overlap": 40}
    ]
}

with open("backend/app/data/market_trends.json", "w") as f:
    json.dump(market_trends, f, indent=2)

# 5. SAMPLE STUDENT RESUMES FOR INSTANT DEMO & TESTING
sample_resumes = [
    {
        "id": "sample-ds-student",
        "name": "Aarav Sharma",
        "title": "3rd Year B.Tech Computer Science & Data Science Student",
        "education": "B.Tech in Computer Science and Engineering, 2022 - 2026 (CGPA: 8.8/10)",
        "experience_years": 0.5,
        "summary": "Enthusiastic undergraduate student with a strong foundation in Data Science, Machine Learning, and Statistical Analysis. Hands-on experience developing predictive models using Scikit-Learn, conducting exploratory data analysis with Pandas and Matplotlib, and querying relational databases using SQL.",
        "skills": ["Python", "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Exploratory Data Analysis", "Data Cleaning", "Statistics", "SQL", "Matplotlib", "Seaborn", "Git"],
        "projects": [
            "Customer Churn Prediction: Implemented classification pipelines using Random Forest and Logistic Regression achieving 87% accuracy with hyperparameter tuning via GridSearchCV.",
            "Exploratory Data Analysis on COVID-19 Trends: Analyzed global infection datasets using Pandas and Seaborn, discovering key seasonal transmission patterns.",
            "Student Performance Analytics Dashboard: Built interactive SQL queries and data visualization reports analyzing academic trends across 5 departments."
        ],
        "extracted_text": """AARAV SHARMA
Third Year B.Tech Computer Science & Engineering
Email: aarav.sharma@example.edu | GitHub: github.com/aarav-ds | LinkedIn: linkedin.com/in/aarav-sharma

EDUCATION
Bachelor of Technology in Computer Science & Engineering
XYZ Institute of Technology, 2022 - 2026 | CGPA: 8.8 / 10.0

TECHNICAL SKILLS
Languages: Python, SQL, C++, Bash
Data Science & Analytics: Pandas, NumPy, Scikit-Learn, Matplotlib, Seaborn, Statistics, Exploratory Data Analysis, Data Cleaning
Machine Learning: Supervised Learning, Random Forest, Logistic Regression, Feature Engineering, Model Evaluation
Tools: Git, GitHub, Jupyter Notebook, VS Code

ACADEMIC & CAPSTONE PROJECTS
1. Customer Churn Prediction System
- Developed end-to-end machine learning pipeline using Python and Scikit-Learn.
- Conducted thorough exploratory data analysis, handled class imbalance with SMOTE, and engineered features.
- Evaluated Random Forest, Decision Trees, and Logistic Regression with 87% ROC-AUC.

2. Global COVID-19 Statistical Analysis & Visualization
- Cleaned and normalized messy epidemiological datasets using Pandas and NumPy.
- Visualized multi-variate correlations and hypothesis testing using Matplotlib and Seaborn.

3. Student Performance Analytics Platform
- Authored complex SQL aggregation queries and window functions across 50,000+ student records.
- Identified drop-out risk factors through statistical inference.
"""
    },
    {
        "id": "sample-web-fullstack",
        "name": "Riya Patel",
        "title": "Full Stack Web & Cloud Enthusiast",
        "education": "B.Tech in Information Technology, 2022 - 2026 (CGPA: 8.5/10)",
        "experience_years": 1.0,
        "summary": "Web developer passionate about building scalable full-stack applications with React, Node.js, and MongoDB. Experienced in containerizing applications with Docker and designing RESTful APIs.",
        "skills": ["JavaScript", "TypeScript", "React", "Node.js", "Express", "MongoDB", "REST APIs", "HTML/CSS", "Docker", "Git", "PostgreSQL", "Linux"],
        "projects": [
            "Campus Placement Portal: Full stack MERN application with role-based JWT authentication, resume upload, and real-time job notifications.",
            "Microservices Task Manager: Built scalable backend services with Node.js, Express, Docker Compose, and Redis caching."
        ],
        "extracted_text": """RIYA PATEL
B.Tech Information Technology | Bangalore, India
Email: riya.patel@example.com | Portfolio: riyapatel.dev

TECHNICAL SKILLS
Frontend: React, JavaScript, TypeScript, HTML/CSS, Tailwind CSS
Backend: Node.js, Express, REST APIs, GraphQL
Databases: MongoDB, PostgreSQL, Redis
DevOps & Cloud: Docker, Git, Linux, GitHub Actions

PROJECTS
1. Campus Placement Management System (MERN Stack)
- Designed full stack web portal using React, Node.js, Express, and MongoDB.
- Implemented secure JWT authentication and role-based access for students and recruiters.

2. Containerized Task Queue Microservice
- Deployed multi-container environment with Docker Compose.
- Implemented Redis caching to reduce database read latency by 60%.
"""
    },
    {
        "id": "sample-ai-engineer",
        "name": "Karan Verma",
        "title": "Aspiring AI & Deep Learning Engineer",
        "education": "B.Tech in Artificial Intelligence & Data Science, 2022 - 2026 (CGPA: 9.1/10)",
        "experience_years": 1.0,
        "summary": "AI enthusiast focused on Deep Learning, Transformers, and Natural Language Processing. Experienced with PyTorch, FastAPI microservices, Docker, and Hugging Face pipelines.",
        "skills": ["Python", "PyTorch", "Transformers", "Natural Language Processing", "Deep Learning", "Neural Networks", "FastAPI", "Docker", "Git", "Scikit-Learn", "Linux"],
        "projects": [
            "Bi-Encoder Semantic Search Engine: Fine-tuned Sentence-Transformers model for domain-specific document search with 89% top-3 precision.",
            "FastAPI Neural Inference Service: Containerized PyTorch model endpoint with asynchronous batching and Docker deployment."
        ],
        "extracted_text": """KARAN VERMA
B.Tech AI & Data Science
Email: karan.verma@example.edu | GitHub: github.com/karan-ai

SKILLS
Deep Learning & AI: PyTorch, Transformers, Natural Language Processing, Neural Networks, Hugging Face
Languages & Backend: Python, FastAPI, REST APIs, SQL
Infrastructure: Docker, Linux, Git, MLflow

PROJECTS
1. Bi-Encoder Semantic Search System
- Implemented sentence embeddings using PyTorch and Hugging Face Transformers.
- Designed vector similarity retrieval scoring against 10,000+ technical documents.

2. Asynchronous Model Inference Gateway
- Built high-throughput API using FastAPI and Uvicorn.
- Packaged model artifacts within Docker containers for lightweight cloud deployment.
"""
    }
]

with open("backend/app/data/sample_resumes.json", "w") as f:
    json.dump(sample_resumes, f, indent=2)

print("All datasets successfully generated!")
