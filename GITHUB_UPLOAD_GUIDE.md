# GitHub 上传完整步骤指南

## 你需要上传的文件结构

```
carbon-aware-ai-scheduling/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── raw/          ← 空文件夹（EIA数据太大，不上传）
│   └── processed/    ← 空文件夹
├── notebooks/
│   ├── 01_data_prep.ipynb
│   ├── 02_descriptive_analysis.ipynb
│   └── 03_predictive_analysis.ipynb
├── src/
│   ├── carbon_proxy.py
│   ├── eia_loader.py
│   ├── models.py
│   └── scheduler_sim.py
└── outputs/
    └── figures/      ← 空文件夹（或放进去你的图）
```

---

## 方法一：GitHub 网页直接上传（最简单，推荐）

### Step 1: 创建 GitHub 账号（已有就跳过）
→ https://github.com/signup

### Step 2: 新建 repository
1. 点右上角 **+** → **New repository**
2. Repository name: `carbon-aware-ai-scheduling`
3. Description: `Reducing AI training carbon footprint through grid-aware workload scheduling — EIA Form 930 analysis`
4. 选 **Public**（让recruiter能看到）
5. ✅ 勾选 **Add a README file**
6. 点 **Create repository**

### Step 3: 上传文件
1. 在repo页面点 **Add file** → **Upload files**
2. 把所有文件拖进去（可以一次选多个）
3. 先上传 `README.md`（会覆盖自动生成的那个）
4. Commit message 写：`Initial commit: descriptive and predictive analysis notebooks`
5. 点 **Commit changes**

### Step 4: 创建文件夹结构
GitHub网页不能直接创建空文件夹，方法是：
- 点 **Add file** → **Create new file**
- 文件名输入：`notebooks/.gitkeep`（这样就创建了notebooks/文件夹）
- 重复操作创建 `src/.gitkeep`、`data/raw/.gitkeep`、`outputs/figures/.gitkeep`

---

## 方法二：用 Git 命令行（更专业）

```bash
# Step 1: 安装 Git（如果没有）
# Mac: brew install git
# Windows: https://git-scm.com/download/win

# Step 2: 在电脑上创建文件夹，把所有文件放进去
mkdir carbon-aware-ai-scheduling
cd carbon-aware-ai-scheduling

# Step 3: 初始化 git
git init
git add .
git commit -m "Initial commit: ESG analytics project — carbon-aware AI scheduling"

# Step 4: 连接到 GitHub（先在GitHub网页创建空repo）
git remote add origin https://github.com/YOUR_USERNAME/carbon-aware-ai-scheduling.git
git branch -M main
git push -u origin main
```

---

## Step 5: 修改 README 中的个人链接

打开 `README.md`，找到最后的 Author 部分，替换：
- `YOUR_USERNAME` → 你的 GitHub username
- `YOUR_PROFILE` → 你的 LinkedIn URL（如 `lin-htet-aung`）

---

## Step 6: 让 repo 更漂亮（可选但推荐）

### 加 Topics 标签
在repo页面，点 ⚙️ 图标（About旁边），加上：
```
python  machine-learning  esg  data-analysis  sustainability  energy  carbon  pandas  scikit-learn  xgboost
```

### 加 Description
```
Carbon-aware AI workload scheduling using EIA hourly grid data. Random Forest forecasting + scenario simulation across 13 U.S. regions.
```

---

## 完成后你的 repo 链接会是：
```
https://github.com/YOUR_USERNAME/carbon-aware-ai-scheduling
```

这个链接直接放进你的：
- CV / LinkedIn 的 Projects 部分
- Cover letter
- Job applications 的 portfolio 链接

---

## 常见问题

**Q: data文件夹里的CSV要上传吗？**  
A: 不需要。数据文件很大（几百MB），而且是公开的EIA数据。README里有下载链接。`.gitignore` 已经设置好不跟踪这些文件。

**Q: 上传了 notebook 但看不到图片怎么办？**  
A: GitHub能预览 `.ipynb` 文件，但图片需要运行后才有。可以把你已经生成的 `.png` 图放进 `outputs/figures/` 文件夹上传。

**Q: 要不要设置成 Private？**  
A: 建议 Public，因为这是给recruiter看的portfolio project。

---

*准备好后，把 GitHub repo 链接发给我，我帮你检查一下是否一切正常。*
