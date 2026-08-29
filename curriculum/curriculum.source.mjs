/**
 * Authored curriculum for "365 Days of AI".
 *
 * This file is the human-edited source of truth for the course structure.
 * `npm run generate:curriculum` compiles it into curriculum/curriculum.yml
 * (deterministic: day numbers, slugs, and IDs are derived here).
 *
 * Structure: 9 sections → 18 subsections → 52 weeks → 365 days.
 * Weeks hold 7 days each; week 52 holds 8 so day 365 (Graduation) lives
 * inside the week hierarchy required by the content layout.
 */

export function slugify(title) {
  return title
    .toLowerCase()
    .replace(/[’']/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .split('-')
    .slice(0, 6)
    .join('-');
}

export const sections = [
  {
    slug: 'computing-foundations',
    title: 'Computing Foundations',
    summary:
      'How computers, operating systems, the command line, networks, and developer tooling actually work — the bedrock every AI practitioner builds on.',
    subsections: [
      {
        slug: 'how-computers-work',
        title: 'How Computers Work',
        summary: 'From transistors to processes: the machine under everything you will build.',
        weeks: [
          {
            theme: 'Inside the Machine',
            project: {
              title: 'Annotated Machine Teardown',
              summary:
                'Inspect your own computer from the command line and produce an annotated one-page architecture diagram of its CPU, memory, storage, and OS, with measured numbers.',
            },
            days: [
              'How a Computer Works: From Transistors to Programs',
              'The CPU: Fetch, Decode, Execute',
              'Memory Hierarchy: Registers, RAM, and Storage',
              'Binary and Data Representation: Bits, Bytes, and Numbers',
              'Text, Images, and Sound as Data',
              'Operating Systems: What They Do and Why',
              'Processes, Threads, and Scheduling',
            ],
          },
          {
            theme: 'The Command Line',
            project: {
              title: 'Personal Automation Script',
              summary:
                'Write and schedule a shell script that organizes a folder of mixed files by type and date, with logging and a dry-run mode.',
            },
            days: [
              'Meet the Terminal: Shells, Prompts, and Commands',
              'Navigating the Filesystem: Paths, Files, and Permissions',
              'Working with Text: cat, grep, sed, and Pipes',
              'Environment Variables and Shell Configuration',
              'Shell Scripting: Variables, Loops, and Conditionals',
              'Package Managers: Homebrew, apt, and winget',
              'Automating Tasks with Shell Scripts and cron',
            ],
          },
        ],
      },
      {
        slug: 'networks-and-the-internet',
        title: 'Networks and the Internet',
        summary: 'How data moves: from DNS lookups to HTTPS, and how to speak to web APIs.',
        weeks: [
          {
            theme: 'How the Internet Works',
            project: {
              title: 'Request Journey Map',
              summary:
                'Trace a real page load end to end with dig, traceroute, curl -v, and browser dev tools, and document every hop and header in a journey diagram.',
            },
            days: [
              'What Happens When You Load a Web Page',
              'IP Addresses, DNS, and Routing',
              'TCP, UDP, and Ports',
              'HTTP: Requests, Responses, and Methods',
              'HTTPS and TLS: Encryption on the Wire',
              'How Browsers Render: HTML, CSS, and JavaScript',
              'Inspecting Traffic with curl and Developer Tools',
            ],
          },
          {
            theme: 'APIs and the Web',
            project: {
              title: 'Weather Command-Line Dashboard',
              summary:
                'Build a shell-based dashboard that pulls a free weather API, handles errors and rate limits, and renders a readable daily report.',
            },
            days: [
              'What an API Is and Why Everything Has One',
              'REST Fundamentals: Resources and Verbs',
              'JSON and Data Serialization',
              'API Authentication: Keys, Tokens, and OAuth',
              'Webhooks and Event-Driven APIs',
              'Rate Limits, Pagination, and Error Handling',
              'Consuming a Public API from the Command Line',
            ],
          },
        ],
      },
      {
        slug: 'developer-workflow',
        title: 'Developer Workflow',
        summary:
          'Version control, editors, and the tooling habits that make everything else faster.',
        weeks: [
          {
            theme: 'Git and GitHub',
            project: {
              title: 'Versioned Notes Repository',
              summary:
                'Create a GitHub repository for your course notes with branches, a merged pull request, a resolved conflict, and a clean commit history.',
            },
            days: [
              'Why Version Control Exists',
              'Git Fundamentals: Repositories, Staging, and Commits',
              'Branching and Merging',
              'Remotes and GitHub',
              'Pull Requests and Code Review',
              'Undoing Things: Reset, Revert, and Reflog',
              'Git Workflows for Real Projects',
            ],
          },
          {
            theme: 'Systems Foundations: Storage, Observability, and Tooling',
            project: {
              title: 'Automated Quality Pipeline',
              summary:
                'Assemble a small repository where formatting, linting, and a smoke test run automatically on every commit via git hooks, with structured logs you can inspect.',
            },
            days: [
              'Choosing and Configuring a Code Editor',
              'Debuggers, Linters, and Formatters',
              'Regular Expressions',
              'Data Storage: Files, Databases, Object Storage, and Caches',
              'Observability: Logs, Metrics, Traces, and Dashboards',
              'Thinking in Automation: Scripts, Hooks, and Pipelines',
              'Section Review: Your Computing Foundations Toolkit',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'programming-with-python',
    title: 'Programming with Python',
    summary:
      'From first program to tested, packaged, database-backed applications — the working programming skill AI work demands.',
    subsections: [
      {
        slug: 'python-basics',
        title: 'Python Basics',
        summary:
          'Syntax, control flow, collections, and functions — fluency through daily practice.',
        weeks: [
          {
            theme: 'Python Setup and First Programs',
            project: {
              title: 'Command-Line Calculator',
              summary:
                'Build a calculator that parses expressions, handles bad input gracefully, and ships with a README and usage examples.',
            },
            days: [
              'Installing Python and Virtual Environments',
              'Variables and Types',
              'Strings and Text Processing',
              'Numbers, Math, and Precision',
              'Input, Output, and f-strings',
              'Reading Error Messages and Debugging',
              'Your First Real Program',
            ],
          },
          {
            theme: 'Control Flow and Collections',
            project: {
              title: 'Terminal Task Manager',
              summary:
                'Build a to-do CLI with add/list/complete/delete commands persisting to a JSON file, using lists and dictionaries idiomatically.',
            },
            days: [
              'Conditionals and Boolean Logic',
              'Loops: for, while, and Iteration Patterns',
              'Lists in Depth',
              'Dictionaries in Depth',
              'Tuples, Sets, and Choosing a Collection',
              'Comprehensions and Iterator Thinking',
              'Building a Data-Driven CLI',
            ],
          },
          {
            theme: 'Functions and Program Design',
            project: {
              title: 'Flashcard Study App',
              summary:
                'Build a spaced-repetition flashcard CLI organized into clean modules with documented functions.',
            },
            days: [
              'Functions: Definition, Arguments, and Return Values',
              'Scope, Closures, and *args/**kwargs',
              'Modules, Imports, and Project Layout',
              'A Tour of the Standard Library',
              'Writing Readable Code',
              'Recursion',
              'Designing a Small Program Well',
            ],
          },
        ],
      },
      {
        slug: 'python-in-practice',
        title: 'Python in Practice',
        summary: 'Files, objects, tests, and automation — Python as a professional tool.',
        weeks: [
          {
            theme: 'Files, Errors, and Object-Oriented Python',
            project: {
              title: 'Expense Tracker',
              summary:
                'Build an expense tracker with CSV import/export, category classes, and monthly summary reports.',
            },
            days: [
              'Reading and Writing Files',
              'CSV and JSON in the Real World',
              'Exceptions and Error Handling Strategy',
              'Classes and Objects',
              'Inheritance, Composition, and Dunder Methods',
              'Dataclasses and Type Hints',
              'Modeling a Domain with Objects',
            ],
          },
          {
            theme: 'Testing and Code Quality',
            project: {
              title: 'Tested Utility Library',
              summary:
                'Publish a small utility library with a full pytest suite, type hints checked by mypy, and CI-style local quality gates.',
            },
            days: [
              'Why Test, and pytest Basics',
              'Fixtures, Parametrization, and Test Design',
              'Test-Driven Development',
              'Mocking and Testing Boundaries',
              'Static Typing with mypy',
              'Linting and Formatting with Ruff',
              'Quality Gates for a Python Project',
            ],
          },
          {
            theme: 'Python for Automation and the Web',
            project: {
              title: 'Personal Automation Toolkit',
              summary:
                'Package three real automations (an API poller, a file organizer, a report generator) as one installable CLI tool.',
            },
            days: [
              'HTTP in Python with requests',
              'Web Scraping Responsibly',
              'Building CLIs with argparse',
              'Scheduling and Background Jobs',
              'A First Web API with FastAPI',
              'Packaging and Distributing Python Code',
              'Shipping an Automation Toolkit',
            ],
          },
        ],
      },
      {
        slug: 'data-and-databases',
        title: 'Data and Databases',
        summary: 'SQL, schema design, ORMs, and the data plumbing behind every AI system.',
        weeks: [
          {
            theme: 'SQL and Relational Databases',
            project: {
              title: 'Personal Library Database',
              summary:
                'Design and query a SQLite database for a book collection: schema, seed data, joins, and a Python reporting script.',
            },
            days: [
              'Relational Databases and SQLite',
              'SELECT: Filtering, Sorting, and Aggregating',
              'Joins and Relationships',
              'Inserting, Updating, and Schema Design',
              'Indexes and Query Performance',
              'SQLite from Python',
              'Designing and Querying a Real Schema',
            ],
          },
          {
            theme: 'Data Formats and Pipelines',
            project: {
              title: 'Section Project: End-to-End Data Pipeline',
              summary:
                'Build a pipeline that ingests a public API, validates records with pydantic, stores them in SQLite via SQLAlchemy, and emits a daily report — tested and logged.',
            },
            days: [
              'Beyond Tables: NoSQL and Key-Value Stores',
              'ORMs and SQLAlchemy',
              'Data Validation with pydantic',
              'Dates, Times, and Time Zones',
              'Concurrency and async Basics',
              'Logging and Configuration',
              'Section Project: A Complete Data Pipeline',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'math-statistics-and-data',
    title: 'Math, Statistics, and Data',
    summary:
      'The linear algebra, calculus, probability, and data-analysis skills that make machine learning understandable rather than magical.',
    subsections: [
      {
        slug: 'mathematics-for-ai',
        title: 'Mathematics for AI',
        summary:
          'Vectors, matrices, gradients, and probability — taught computationally with NumPy.',
        weeks: [
          {
            theme: 'Linear Algebra I: Vectors and Matrices',
            project: {
              title: 'Image Transformer',
              summary:
                'Use NumPy matrix operations to rotate, scale, and shear images, demonstrating linear transformations visually.',
            },
            days: [
              'Vectors: Direction, Magnitude, and Meaning',
              'Matrices and What They Represent',
              'Matrix Multiplication',
              'Linear Transformations',
              'Dot Products and Similarity',
              'NumPy: Arrays and Vectorized Thinking',
              'Transforming Images with Matrices',
            ],
          },
          {
            theme: 'Linear Algebra II and Calculus',
            project: {
              title: 'Gradient Descent Visualizer',
              summary:
                'Implement gradient descent from scratch and animate its path across 2D loss surfaces, including a pathological case.',
            },
            days: [
              'Eigenvalues and Eigenvectors, Intuitively',
              'Norms, Distances, and Similarity Measures',
              'Derivatives: Rates of Change',
              'Partial Derivatives and Gradients',
              'The Chain Rule',
              'Gradient Descent from Scratch',
              'Visualizing Optimization',
            ],
          },
          {
            theme: 'Probability and Statistics',
            project: {
              title: 'A/B Test Analyzer',
              summary:
                'Analyze a simulated experiment end to end: hypothesis, test statistic, confidence interval, and a plain-language verdict.',
            },
            days: [
              'Probability: Events, Rules, and Intuition',
              'Random Variables and Distributions',
              'Bayes’ Theorem',
              'Descriptive Statistics That Don’t Lie',
              'Sampling and the Central Limit Theorem',
              'Hypothesis Tests and Confidence Intervals',
              'Analyzing an Experiment End to End',
            ],
          },
        ],
      },
      {
        slug: 'data-analysis',
        title: 'Data Analysis',
        summary: 'pandas, visualization, and the craft of honest exploratory data analysis.',
        weeks: [
          {
            theme: 'pandas and Data Wrangling',
            project: {
              title: 'Messy Dataset Rescue',
              summary:
                'Take a genuinely messy public dataset and produce a documented, reproducible cleaning notebook with before/after data-quality checks.',
            },
            days: [
              'pandas: Series and DataFrames',
              'Loading and Inspecting Data',
              'Selecting and Filtering',
              'Groupby and Aggregation',
              'Merging and Reshaping',
              'Cleaning Messy Data',
              'A Reproducible Cleaning Pipeline',
            ],
          },
          {
            theme: 'Data Visualization',
            project: {
              title: 'Exploratory Analysis Report',
              summary:
                'Produce a narrated EDA report on a real dataset with at least five well-chosen, honestly-scaled charts.',
            },
            days: [
              'Why We Visualize, and Choosing the Right Chart',
              'Matplotlib Fundamentals',
              'Statistical Plots with seaborn',
              'Distributions and Relationships',
              'Time Series Visualization',
              'Visual Storytelling and Chart Honesty',
              'Building an EDA Report',
            ],
          },
          {
            theme: 'Working with Real Data',
            project: {
              title: 'Section Project: Full Exploratory Study',
              summary:
                'Choose a public dataset, pose three questions, and deliver a reproducible notebook answering them with cleaned data, statistics, and visuals.',
            },
            days: [
              'Finding Data: Open Datasets and APIs',
              'From API to DataFrame',
              'The Exploratory Data Analysis Process',
              'Thinking in Features',
              'Data Ethics, Bias, and Provenance',
              'Reproducible Notebooks',
              'Section Project: An Exploratory Study',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'machine-learning',
    title: 'Machine Learning',
    summary:
      'Classical machine learning done properly: models, evaluation, feature work, and the discipline that separates working systems from leaderboard tricks.',
    subsections: [
      {
        slug: 'core-concepts',
        title: 'Core Concepts',
        summary: 'The ML workflow, generalization, and your first models with scikit-learn.',
        weeks: [
          {
            theme: 'Machine Learning Fundamentals',
            project: {
              title: 'First End-to-End Model',
              summary:
                'Train, evaluate, and document a classifier on the iris dataset with a proper train/test protocol and an honest error analysis.',
            },
            days: [
              'What Machine Learning Is and Is Not',
              'Supervised, Unsupervised, and Reinforcement Learning',
              'The Machine Learning Workflow',
              'Train, Validation, and Test Splits',
              'Overfitting and Underfitting',
              'Your First Model with scikit-learn',
              'An End-to-End Classification Exercise',
            ],
          },
          {
            theme: 'Regression',
            project: {
              title: 'House Price Model',
              summary:
                'Build a regularized regression model on a housing dataset with feature analysis and residual diagnostics.',
            },
            days: [
              'Linear Regression',
              'Loss Functions and Least Squares',
              'Multiple and Polynomial Regression',
              'Regularization: Ridge and Lasso',
              'Regression Metrics',
              'Linear Regression from Scratch',
              'A Complete Regression Project',
            ],
          },
          {
            theme: 'Classification',
            project: {
              title: 'Spam Classifier',
              summary:
                'Build a text spam classifier with proper handling of class imbalance and a precision/recall trade-off analysis.',
            },
            days: [
              'Logistic Regression',
              'Decision Boundaries',
              'k-Nearest Neighbors',
              'Naive Bayes and Text Classification',
              'Precision, Recall, ROC, and Choosing Thresholds',
              'Class Imbalance',
              'A Complete Classification Project',
            ],
          },
        ],
      },
      {
        slug: 'supervised-learning',
        title: 'Supervised Learning in Depth',
        summary: 'Trees, ensembles, SVMs, feature engineering, and rigorous evaluation.',
        weeks: [
          {
            theme: 'Trees and Ensembles',
            project: {
              title: 'Tabular Challenge',
              summary:
                'Compete against your own baseline on a tabular dataset: tuned gradient boosting versus a linear model, with a documented comparison.',
            },
            days: [
              'Decision Trees',
              'Random Forests',
              'Gradient Boosting',
              'XGBoost and LightGBM in Practice',
              'Hyperparameter Tuning',
              'Cross-Validation Done Right',
              'Winning on Tabular Data',
            ],
          },
          {
            theme: 'Features and Support Vector Machines',
            project: {
              title: 'Feature Engineering Challenge',
              summary:
                'Improve a fixed model’s performance purely through feature work on a raw dataset, documenting each feature’s measured impact.',
            },
            days: [
              'Support Vector Machines',
              'Feature Scaling and Encoding',
              'Feature Engineering',
              'Feature Selection',
              'scikit-learn Pipelines',
              'Handling Missing Data',
              'Features Beat Algorithms',
            ],
          },
          {
            theme: 'Evaluation and Interpretation',
            project: {
              title: 'Model Audit Report',
              summary:
                'Audit a trained model for leakage, fairness, and failure modes, and write a decision-ready model report.',
            },
            days: [
              'Choosing the Right Metric',
              'Learning Curves and Diagnostics',
              'Interpreting Models: Importances and SHAP',
              'Fairness and Bias in Models',
              'Data Leakage',
              'Baselines and Error Analysis',
              'Writing a Model Report',
            ],
          },
        ],
      },
      {
        slug: 'beyond-supervised',
        title: 'Beyond Supervised Learning',
        summary: 'Clustering, dimensionality reduction, recommenders, and ML as a practiced craft.',
        weeks: [
          {
            theme: 'Unsupervised Learning',
            project: {
              title: 'Customer Segmentation',
              summary:
                'Cluster a customer dataset, reduce it for visualization, name the segments, and defend the number of clusters chosen.',
            },
            days: [
              'Clustering with k-means',
              'Hierarchical Clustering and DBSCAN',
              'Principal Component Analysis',
              't-SNE and UMAP',
              'Anomaly Detection',
              'Recommender Systems',
              'A Segmentation Study',
            ],
          },
          {
            theme: 'Machine Learning in Practice',
            project: {
              title: 'Section Project: Deployed ML Service',
              summary:
                'Train, persist, and serve a model behind a FastAPI endpoint with input validation, tests, and a monitoring plan.',
            },
            days: [
              'The ML Project Lifecycle',
              'Building Datasets and Labeling',
              'Time Series Forecasting Basics',
              'Saving and Versioning Models',
              'Serving a Model over an API',
              'Monitoring Models in Production',
              'Section Project: An ML Service',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'deep-learning',
    title: 'Deep Learning',
    summary:
      'Neural networks from first principles to transformers: build them, train them, debug them, and understand the hardware they run on.',
    subsections: [
      {
        slug: 'neural-networks',
        title: 'Neural Networks',
        summary: 'Backpropagation, PyTorch, and the craft of training deep models.',
        weeks: [
          {
            theme: 'Neural Network Foundations',
            project: {
              title: 'MNIST from Scratch',
              summary:
                'Implement a two-layer neural network in pure NumPy that reaches at least 95% accuracy on MNIST digits.',
            },
            days: [
              'The Perceptron',
              'Activation Functions',
              'Forward Propagation',
              'Backpropagation',
              'A Neural Network in Pure NumPy',
              'PyTorch Tensors',
              'Training MNIST from Scratch',
            ],
          },
          {
            theme: 'Training Deep Networks',
            project: {
              title: 'Fashion-MNIST Classifier',
              summary:
                'Train a PyTorch classifier with a proper training loop, LR schedule, and regularization, beating a stated baseline.',
            },
            days: [
              'PyTorch: autograd and nn.Module',
              'Datasets and DataLoaders',
              'Optimizers: SGD to Adam',
              'Learning Rate Schedules',
              'Dropout, Batch Norm, and Regularization',
              'Debugging Training Runs',
              'A Disciplined Training Project',
            ],
          },
          {
            theme: 'Convolutional Networks and Vision',
            project: {
              title: 'Custom Image Classifier',
              summary:
                'Fine-tune a pretrained CNN on your own small image dataset with augmentation and an error-case gallery.',
            },
            days: [
              'Convolutions',
              'CNN Architectures',
              'Transfer Learning',
              'Data Augmentation',
              'Training a Vision Model End to End',
              'Beyond Classification: Detection and Segmentation',
              'Your Own Image Classifier',
            ],
          },
        ],
      },
      {
        slug: 'sequence-models-and-transformers',
        title: 'Sequence Models and Transformers',
        summary: 'From word vectors to attention: the architecture behind modern AI.',
        weeks: [
          {
            theme: 'Sequences and Text',
            project: {
              title: 'Sentiment Analyzer',
              summary:
                'Build a review-sentiment model comparing bag-of-words, embeddings, and a small recurrent network.',
            },
            days: [
              'Text Preprocessing and Tokenization',
              'Word Embeddings',
              'Recurrent Neural Networks',
              'LSTMs and GRUs',
              'Sequence-to-Sequence and Early Attention',
              'Text Classification with Embeddings',
              'A Sentiment Analysis Project',
            ],
          },
          {
            theme: 'Transformers',
            project: {
              title: 'Fine-Tuned Transformer',
              summary:
                'Fine-tune a small pretrained transformer on a text classification task with Hugging Face and report results honestly.',
            },
            days: [
              '“Attention Is All You Need”',
              'Self-Attention, Step by Step',
              'The Transformer Architecture',
              'Encoder Models: BERT and Friends',
              'Decoder Models: The GPT Family',
              'Hugging Face Transformers in Practice',
              'Fine-Tuning a Small Transformer',
            ],
          },
          {
            theme: 'Training at Scale',
            project: {
              title: 'Section Project: Reproduce a Result',
              summary:
                'Reproduce a small published deep-learning result end to end, with experiment tracking and a reproduction report.',
            },
            days: [
              'GPUs and AI Hardware',
              'Mixed Precision and Performance',
              'Distributed Training Concepts',
              'Experiment Tracking',
              'Quantization and Distillation',
              'Scaling Laws and What They Bought Us',
              'Section Project: Reproducing a Paper',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'llms-and-generative-ai',
    title: 'LLMs and Generative AI',
    summary:
      'Large language models as a working material: how they are made, how to prompt and call them, how to ground them with retrieval, customize them, and go multimodal.',
    subsections: [
      {
        slug: 'working-with-llms',
        title: 'Working with LLMs',
        summary: 'The model landscape, prompting as engineering, and LLM APIs in production.',
        weeks: [
          {
            theme: 'The LLM Landscape',
            project: {
              title: 'Model Comparison Study',
              summary:
                'Design a ten-task benchmark and compare two accessible models on it, documenting failure patterns and cost.',
            },
            days: [
              'How Large Language Models Are Trained',
              'Pretraining, Fine-Tuning, and RLHF',
              'The Model Landscape: Claude, GPT, Gemini, Llama',
              'Open Weights versus Closed APIs',
              'Tokens, Context Windows, and Sampling',
              'Capabilities, Limits, and Hallucination',
              'Benchmarking Models Yourself',
            ],
          },
          {
            theme: 'Prompt Engineering',
            project: {
              title: 'Reusable Prompt Library',
              summary:
                'Build a tested library of parameterized prompts for five recurring tasks, each with evaluation examples.',
            },
            days: [
              'Prompting Fundamentals',
              'System Prompts and Role Design',
              'Few-Shot Examples and Chain of Thought',
              'Structured Output: Getting Reliable JSON',
              'Prompt Patterns and Templates',
              'Prompt Injection and Safe Prompting',
              'A Tested Prompt Library',
            ],
          },
          {
            theme: 'LLM APIs',
            project: {
              title: 'Command-Line AI Assistant',
              summary:
                'Build a streaming CLI assistant with conversation memory, tool use, and a cost meter.',
            },
            days: [
              'First Calls to the Claude API',
              'The OpenAI-Compatible Ecosystem',
              'Streaming Responses',
              'Tool Use and Function Calling',
              'Working with Images and Documents',
              'Cost, Caching, and Rate Limits',
              'Building a CLI Assistant',
            ],
          },
        ],
      },
      {
        slug: 'retrieval-and-customization',
        title: 'Retrieval and Customization',
        summary: 'Embeddings, vector search, RAG, fine-tuning, and running models locally.',
        weeks: [
          {
            theme: 'Embeddings and Vector Search',
            project: {
              title: 'Semantic Search Engine',
              summary:
                'Build semantic search over your own notes with embeddings, a vector store, and a retrieval-quality evaluation.',
            },
            days: [
              'What Embeddings Are',
              'Semantic Similarity Search',
              'Vector Databases',
              'Chunking Strategies',
              'Hybrid Search and Rerankers',
              'Evaluating Retrieval Quality',
              'Semantic Search over Your Own Notes',
            ],
          },
          {
            theme: 'Retrieval-Augmented Generation',
            project: {
              title: 'Documentation Q&A Bot',
              summary:
                'Build a RAG assistant over a real documentation set with citations and a measured answer-quality eval.',
            },
            days: [
              'The RAG Architecture',
              'A Minimal RAG System from Scratch',
              'RAG over PDFs and Messy Documents',
              'Citations and Grounded Answers',
              'Advanced RAG Patterns',
              'Evaluating RAG Systems',
              'A Documentation Assistant',
            ],
          },
          {
            theme: 'Customizing and Running Models',
            project: {
              title: 'Local Fine-Tuned Model',
              summary:
                'Fine-tune a small open model with LoRA on a task dataset and serve it locally, comparing before and after.',
            },
            days: [
              'Prompting versus RAG versus Fine-Tuning',
              'Fine-Tuning with LoRA',
              'Building Fine-Tuning Datasets',
              'Running Local Models with Ollama',
              'Quantized Inference and llama.cpp',
              'Serving Open Models',
              'Fine-Tune and Serve Your Own Model',
            ],
          },
        ],
      },
      {
        slug: 'multimodal-and-frontier',
        title: 'Multimodal and Frontier',
        summary: 'Image, speech, video, and the ethics of generative media.',
        weeks: [
          {
            theme: 'Multimodal and Generative Media',
            project: {
              title: 'Section Project: Multimodal App',
              summary:
                'Build an application combining at least two modalities — for example, speech in, grounded text out, generated image alongside.',
            },
            days: [
              'How Diffusion Models Generate Images',
              'Image Generation in Practice',
              'Speech: Recognition and Synthesis',
              'Video and Music Generation',
              'Multimodal Models',
              'Generative AI Ethics and Copyright',
              'Section Project: A Multimodal Application',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'ai-engineering',
    title: 'AI Engineering: Agents and Applications',
    summary:
      'Agents, MCP, AI coding tools, evaluation, and full-stack AI applications — engineering AI systems that hold up in production.',
    subsections: [
      {
        slug: 'agents-and-tools',
        title: 'Agents and Tools',
        summary:
          'The agent loop, the Model Context Protocol, and AI coding agents as force multipliers.',
        weeks: [
          {
            theme: 'AI Agents',
            project: {
              title: 'Research Agent',
              summary:
                'Build an agent that researches a question with search and note-taking tools and produces a cited brief.',
            },
            days: [
              'What an AI Agent Is',
              'The Agent Loop: Reason, Act, Observe',
              'Designing Tools for Agents',
              'An Agent from Scratch',
              'Agent Frameworks and When to Use Them',
              'Multi-Agent Systems',
              'Building a Research Agent',
            ],
          },
          {
            theme: 'The Model Context Protocol',
            project: {
              title: 'Personal MCP Server',
              summary:
                'Build and test an MCP server exposing your own data or tools, and use it from a real client.',
            },
            days: [
              'What MCP Is and Why It Exists',
              'Using MCP Servers',
              'Building an MCP Server',
              'MCP Resources and Prompts',
              'Building an MCP Client',
              'MCP Security',
              'Your Personal MCP Server',
            ],
          },
          {
            theme: 'AI Coding Agents',
            project: {
              title: 'Agent-Built Feature',
              summary:
                'Ship a reviewed, tested feature to one of your own projects using an AI coding agent, documenting the workflow.',
            },
            days: [
              'The AI Coding Landscape',
              'Working with a Coding Agent',
              'Effective Agentic Coding Workflows',
              'Configuring Agents: Memory, Skills, and Rules',
              'Reviewing and Trusting AI-Written Code',
              'Coding Agents in CI and Automation',
              'Shipping a Feature with an Agent',
            ],
          },
        ],
      },
      {
        slug: 'production-ai-systems',
        title: 'Production AI Systems',
        summary: 'Evaluation, observability, full-stack architecture, and production retrieval.',
        weeks: [
          {
            theme: 'Evaluation and Reliability',
            project: {
              title: 'Evaluation Harness',
              summary:
                'Build an eval harness with a labeled dataset, an LLM judge, and regression gates for one of your AI features.',
            },
            days: [
              'Why Evals Are the Real Moat',
              'Building Evaluation Datasets',
              'LLM-as-Judge',
              'Regression Testing for Prompts and Models',
              'Guardrails and Content Moderation',
              'Observability and Tracing for AI',
              'An Evaluation Harness',
            ],
          },
          {
            theme: 'Full-Stack AI Applications',
            project: {
              title: 'Full-Stack AI App',
              summary:
                'Build a deployed chat application with streaming, auth, usage quotas, and a vendor-abstraction layer.',
            },
            days: [
              'Architecture of an AI Product',
              'Backend Patterns for LLM Apps',
              'Chat UX and Streaming Frontends',
              'Auth, Quotas, and Billing',
              'Latency and Caching',
              'Vendor Abstraction and Fallbacks',
              'A Full-Stack AI Application',
            ],
          },
          {
            theme: 'Production Retrieval and Pipelines',
            project: {
              title: 'Section Project: Production Assistant',
              summary:
                'Assemble a production-grade assistant: ingestion pipeline, fresh index, evals, cost budget, and privacy review.',
            },
            days: [
              'Data Ingestion Pipelines',
              'Document Processing at Scale',
              'Keeping Indexes Fresh',
              'Scaling Retrieval',
              'Cost Engineering for AI Systems',
              'Privacy in AI Systems',
              'Section Project: A Production Assistant',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'deployment-mlops-and-security',
    title: 'Deployment, MLOps, and Security',
    summary:
      'Containers, cloud, CI/CD, monitoring, and the security discipline AI systems demand in the real world.',
    subsections: [
      {
        slug: 'deploying-ai-systems',
        title: 'Deploying AI Systems',
        summary: 'Docker, Kubernetes concepts, cloud options, and operating AI in production.',
        weeks: [
          {
            theme: 'Containers and Cloud',
            project: {
              title: 'Containerized Deployment',
              summary:
                'Containerize an AI app with Docker Compose and a CI pipeline that builds, tests, and publishes the image.',
            },
            days: [
              'Docker Fundamentals',
              'Dockerizing an AI Application',
              'Docker Compose for Multi-Service Apps',
              'Kubernetes Concepts',
              'Cloud Options and Free Tiers',
              'CI/CD with GitHub Actions',
              'A Containerized AI Deployment',
            ],
          },
          {
            theme: 'Operating AI in Production',
            project: {
              title: 'Monitored Deployment',
              summary:
                'Deploy a service to a free-tier cloud host with dashboards, alerts, and a written rollback procedure.',
            },
            days: [
              'Deploying to a Cloud Service',
              'GPU Serving and Inference Infrastructure',
              'Monitoring and Alerting',
              'Logging and Analytics for AI Features',
              'Rollouts, A/B Tests, and Feature Flags',
              'Incidents and Rollbacks',
              'A Monitored Production Deployment',
            ],
          },
        ],
      },
      {
        slug: 'securing-ai-systems',
        title: 'Securing AI Systems',
        summary: 'Threat modeling, prompt-injection defense, privacy, and governance.',
        weeks: [
          {
            theme: 'AI Security and Privacy',
            project: {
              title: 'Section Project: Security Review',
              summary:
                'Threat-model and security-review your own AI application, produce findings with severities, and fix the top three.',
            },
            days: [
              'Threat Modeling AI Systems',
              'Defending Against Prompt Injection',
              'Data Privacy and PII Handling',
              'Model and Supply Chain Security',
              'AI Governance and Regulation',
              'Red Teaming Your Own Systems',
              'Section Project: A Security Review',
            ],
          },
        ],
      },
    ],
  },
  {
    slug: 'capstone',
    title: 'Capstone',
    summary:
      'Two weeks to design, build, evaluate, secure, deploy, and present a complete AI application of your own.',
    subsections: [
      {
        slug: 'capstone-project',
        title: 'Capstone Project',
        summary: 'Everything you learned, shipped as one real product.',
        weeks: [
          {
            theme: 'Capstone Build I: Foundation',
            project: {
              title: 'Capstone Milestone 1',
              summary:
                'A scoped design document plus a working vertical slice: data layer, core AI feature, and a passing eval baseline.',
            },
            days: [
              'Choosing and Scoping Your Capstone',
              'Architecture and Design Document',
              'Data and Retrieval Layer',
              'Core AI Features',
              'Agent and Tool Integration',
              'Tests and Evals for Your Capstone',
              'Milestone Review and Course Correction',
            ],
          },
          {
            theme: 'Capstone Build II: Ship It',
            project: {
              title: 'Capstone Final Delivery',
              summary:
                'The finished capstone: deployed, monitored, security-reviewed, documented, and demonstrated.',
            },
            days: [
              'Frontend and User Experience',
              'Deploying Your Capstone',
              'Monitoring and Cost Controls',
              'Security Review of Your Capstone',
              'Documentation and Demo',
              'Portfolio, Resume, and Sharing Your Work',
              'Capstone Retrospective',
              'Graduation: Your AI Roadmap Going Forward',
            ],
          },
        ],
      },
    ],
  },
];
