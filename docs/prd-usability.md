# PRD · 砂川平和ひろば公開記事アーカイブ 易用性改进

| 字段 | 值 |
| -- | -- |
| Project key | SUNA |
| 版本 | v1 · 2026-09-28 |
| 负责人 | 维护者（tera） |
| 状态 | Draft |
| 依据 | `audit/sunagawa-ui-usability-review-2026-09-28.md`、`audit/sunagawa-archive-audit-3-2026-09-27.md` |
| 规模 | 6 个 Epic · 17 个 Story · 共 38 story points |
| 导入文件 | `specs/sunagawa-ux-jira-import.csv`（Jira CSV 导入） |

## 1. 背景与问题

首页 / 记事一览拆分（2026-09 下旬）之后，站点的结构问题基本解决。剩下的问题有一个共同原因：**页面上的导航、筛选器、说明先于内容出现，而且占的面积更大。**

| 实测指标 | 当前值 | 目标 |
| -- | -- | -- |
| 手机文章页：正文第一段位置 | y=798（屏高 812，首屏无正文） | 首屏内，H1 ≤ 200px |
| 手机 header 高度 | 520–540px | ≤ 120px |
| 桌面 archive：输入关键词后可见反馈 | 无（件数 y≈820，结果 y=1,275） | 不滚动即可见件数 |
| 手机筛选区高度 | ≈477px（种类 + 语言） | ≤ 250px（三组合计） |
| 桌面吸顶区高度 | ≈265px（视口 1/3） | ≤ 72px |
| 手机 archive 页总高 | 36,665px（45 屏） | ≤ 18,000px |
| 搜「伊達判決」前 5 条中标题命中数 | 按日期排，解说类在第 19 条之后 | ≥ 3 |
| 授权状态说明 | 全站 0 处 | about + 首页 + changelog |

## 2. 目标与非目标

**目标**

1. 手机上任何页面的首屏都是内容，不是导航
2. 检索的每一次操作都有可见反馈
3. 从搜索引擎进来的读者知道自己在一个保存副本里，并能找到同类文章
4. 公开说明授权状态

**非目标**

* 在首页或编辑页引入档案图片——必须等 SUNA-23 之后再评估
* EN / JA 语言切换按钮——不承诺一个并不存在的完整英文版
* 重做配色、字体、品牌——现有暖白 + 墨绿方案保留
* 为 208 篇文章补写真实的 alt 文本——另开 a11y 史诗
* Wayback Machine 批量交叉存档——另开运维任务
* 引入 CMS、构建框架或第三方检索服务——保持零外部依赖的静态站

## 3. 用户角色

| 角色 | 是谁 | 他们要什么 |
| -- | -- | -- |
| **初访者** | 第一次听说砂川、被朋友或老师推荐来的人 | 30 秒内知道这是什么、从哪开始读 |
| **研究者 / 学生** | 写报告或论文，要找特定主题的一手记录 | 输入关键词，马上看到相关文章，能引用 |
| **搜索引擎来访者** | 从 Google 直接落在某一篇文章页 | 知道自己在一个保存副本里，能找到同类文章 |
| **手机读者** | 在通勤路上用手机读 | 首屏就是内容，不被导航和筛选器淹没 |
| **关系者 / 权利人** | ひろば成员或文章中出现的人 | 知道这个副本的授权状态，知道找谁更正 |
| **维护者** | 站点作者本人 | 改动小、风险低、不引入依赖 |

## 4. 约束

* 纯静态站（GitHub Pages），不引入外部 JS / CSS 库，不引入构建框架
* 现有 URL 参数（`q` / `type` / `language` / `year`）与文章 URL 必须保持兼容
* 深色模式、`localStorage.theme` 键名、页脚「訂正・削除依頼」链接保持不变
* 编辑立场不变：不改写原文，只改导航与呈现

## 5. Epic 与 Story

格式说明：每个 Story 都按 Jira 字段书写。验收标准用 Given / When / Then；**Story Points** 用 Fibonacci；**Priority** 用 Jira 默认五级。

### SUNA-1 · Epic：手机端导航瘦身：让每个页面的首屏回到内容

* **Issue Type**：Epic
* **Labels**：ux, mobile
* **Story 数 / Points**：2 / 7
* **背景**：手机上导航区当前高 520–540px（屏高 812），文章页首屏看不到正文。把导航收起，让内容进入首屏。

#### SUNA-7 · 手机端导航收进「メニュー」按钮

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-1 |
| Priority | Highest（P0） |
| Story Points | 5 |
| Labels | mobile, nav, a11y |

**User Story**

> 作为**用手机从搜索引擎进入文章页的读者**，我想打开页面时第一屏就能看到标题和正文，以便不用先滑过 9 个导航链接才开始阅读。

**Acceptance Criteria**

1. **Given** 视口宽度 < 768px，**When** 打开任意文章页，**Then** header 高度 ≤ 120px；H1 顶部 y ≤ 200px；正文第一段出现在首屏内（y < 812）
2. **Given** 视口宽度 < 768px，**When** 点击「メニュー / Menu」按钮，**Then** 展开全部 9 个导航链接；按钮 aria-expanded=true；焦点移入菜单
3. **Given** 菜单已展开，**When** 按 Esc、再次点击按钮或点击菜单外区域，**Then** 菜单收起，焦点回到按钮
4. **Given** 视口宽度 ≥ 768px，**When** 打开任意页面，**Then** 导航保持现有两层横排，不出现菜单按钮

**Notes**：影响全部页面模板（首页、archive、编辑页 9 个、文章页 208 个、404）。不使用外部 JS 库。

#### SUNA-8 · 主题切换压缩为单个图标按钮

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-1 |
| Priority | High（P1） |
| Story Points | 2 |
| Labels | mobile, nav |

**User Story**

> 作为**手机读者**，我想主题切换不占一整行，以便首屏空间留给内容。

**Acceptance Criteria**

1. **Given** 任意页面，**When** 点击主题按钮，**Then** 按 Light → Dark → Auto 循环；aria-label 与 title 显示当前状态（例：「表示：ダーク / Theme: Dark」）
2. **Given** 已选 Dark，**When** 跳转到其他任意页面，**Then** 仍为 Dark（沿用 localStorage 键 theme，不改存储格式）
3. **Given** 手机端，**When** 测量按钮，**Then** 点击区域 ≥ 44×44px

**Notes**：可与 SUNA-7 同一个 PR：按钮放在 header 右上角，与菜单按钮并排。

---

### SUNA-2 · Epic：首页入口：减少一次点击，引导到对的地方

* **Issue Type**：Epic
* **Labels**：ux, home
* **Story 数 / Points**：4 / 5
* **背景**：首页拆分后结构已清爽，剩下的问题是：主任务（检索）还要多点一次；定位声明挡在主按钮前；新手入口排序不当；联系邮箱容易发错。

#### SUNA-9 · 首页直接放检索框，提交后跳转记事一览

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-2 |
| Priority | High（P1） |
| Story Points | 2 |
| Labels | home, search |
| Blocked by | SUNA-7 |

**User Story**

> 作为**想查某个主题的研究者或学生**，我想在首页直接输入关键词，以便不用先点「全208件」按钮再找检索框。

**Acceptance Criteria**

1. **Given** 首页，**When** 输入「伊達判決」并按 Enter 或点「検索」，**Then** 跳转到 archive.html?q=伊達判決，结果已筛好
2. **Given** 首页检索框为空，**When** 提交，**Then** 跳转到 archive.html（不带 q 参数）
3. **Given** 手机 375×812（SUNA-7 完成后），**When** 打开首页，**Then** 检索框完整出现在首屏内
4. **Given** 屏幕阅读器，**When** 聚焦检索框，**Then** 读出可见 label「記事検索 / Search articles」

**Notes**：「全208件の記事を検索・閲覧する」按钮保留，放在检索框旁，作为浏览入口。纯 HTML form（GET），无需 JS。

#### SUNA-10 · 首页正文里的ひろば邮箱改标签，避免发错对象

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-2 |
| Priority | High（P1） |
| Story Points | 1 |
| Labels | home, contact |

**User Story**

> 作为**发现保存页有错字、想联系档案维护者的读者**，我想一眼分清哪个邮箱是档案的、哪个是ひろば本体的，以便不会把档案的更正请求发到ひろば。

**Acceptance Criteria**

1. **Given** 首页「Official links / 公式リンク」区，**When** 查看联系行，**Then** 文字为「ひろば本体への連絡 / Contact Sunagawa Heiwa Hiroba · sunagawa.heiwa@gmail.com」
2. **Given** 首页，**When** 查找档案联系方式，**Then** 页脚保留 zezelunar@gmail.com 与「訂正・削除依頼」链接，文字不变

**Notes**：只改一行文案。

#### SUNA-11 · 定位声明降权，挪到简介段之后

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-2 |
| Priority | Medium（P2） |
| Story Points | 1 |
| Labels | home, copy |

**User Story**

> 作为**第一次来的访客**，我想进门先看到这个站能做什么，再看到它不是什么，以便不会觉得一进门就被警告。

**Acceptance Criteria**

1. **Given** 首页，**When** 从上往下读，**Then** 顺序为：H1 → 副标题 → 主按钮 / 检索框 → 简介段 → 定位声明
2. **Given** 首页，**When** 查看定位声明，**Then** 文案一字不改；字重为普通（非 bold），字号不小于正文的 0.875 倍

#### SUNA-12 · 「砂川闘争年表」改为主题卡，替换「現地を歩く」

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-2 |
| Priority | Medium（P2） |
| Story Points | 1 |
| Labels | home, ia |

**User Story**

> 作为**对砂川一无所知的新手**，我想从主题卡就能进入 1609–1977 的通史年表，以便先有全局时间线，再去读单篇文章。

**Acceptance Criteria**

1. **Given** 首页「テーマから探す」，**When** 查看卡片，**Then** 仍为 6 张、3×2 网格；含「砂川闘争年表」卡，标签为「年表」，链接 sunagawa-history.html
2. **Given** 首页，**When** 查看国賠訴訟年表卡，**Then** 标签改为「訴訟」，避免两张卡都叫「年表」
3. **Given** guide.html#walk-the-site，**When** 从 guide 页访问，**Then** 锚点保留、仍可到达（入口从首页卡片移到 guide 页内）

**Notes**：卡片下方那行「砂川闘争年表 · Research guide」文字链接中，年表一项删除，Research guide 保留。

---

### SUNA-3 · Epic：检索与筛选：输入即见反馈，筛选不压住结果

* **Issue Type**：Epic
* **Labels**：ux, search
* **Story 数 / Points**：6 / 15
* **背景**：记事一览是全站核心任务。当前输入关键词后视口内无变化；筛选区 28 个 chip 占 0.6 屏；结果只按日期排序。

#### SUNA-13 · 结果件数与「すべて解除」移到检索框正下方

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | Highest（P0） |
| Story Points | 2 |
| Labels | search, feedback |

**User Story**

> 作为**在记事一览输入关键词的研究者**，我想输入后立刻看到命中了多少条，以便知道检索起了作用，而不是以为页面没反应。

**Acceptance Criteria**

1. **Given** 桌面 1280×800，archive.html 未滚动，**When** 在检索框输入「伊達判決」，**Then** 不滚动即可在视口内看到「45件」计数
2. **Given** 任意筛选状态，**When** 查看件数行，**Then** 件数行紧贴检索框下方；「Reset all filters / すべて解除」与件数同一行右对齐
3. **Given** 屏幕阅读器，**When** 输入关键词，**Then** aria-live 区域播报件数（保留现有行为）

**Notes**：当前件数行夹在「種類」和「年別」两组之间（桌面 y≈820，首条结果 y=1,275）。

#### SUNA-14 · 筛选顺序改为 种类 → 年份 → 语言，语言组折叠

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | High（P1） |
| Story Points | 3 |
| Labels | search, filters, mobile |

**User Story**

> 作为**用手机筛选文章的读者**，我想筛选区不要占掉大半屏，以便选完条件马上能看到结果。

**Acceptance Criteria**

1. **Given** archive.html，**When** 查看筛选区，**Then** 从上到下依次为：種類 → 年別 → 記事の言語
2. **Given** 手机 375×812，**When** 打开 archive.html，**Then** 筛选区（种类 + 年份 + 语言）总高度 ≤ 250px（当前约 477px 仅种类 + 语言两组）
3. **Given** 语言组，**When** 默认状态，**Then** 折叠为一个下拉或「言語：すべて ▾」按钮；展开后各选项仍显示件数，0 件选项 disabled
4. **Given** 任意筛选组合，**When** 刷新或分享 URL，**Then** type / language / year 参数名与取值不变，现有链接全部仍可用

**Notes**：手机端年份已经是下拉，沿用同一组件。

#### SUNA-15 · 合并吸顶区为一条，修复两层吸顶间的文字透出

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | High（P1） |
| Story Points | 3 |
| Labels | search, sticky, bug |
| Blocked by | SUNA-14 |

**User Story**

> 作为**滚动浏览检索结果的读者**，我想吸顶的检索栏又薄又完整，以便随时能改关键词，又不挡住内容。

**Acceptance Criteria**

1. **Given** 桌面 1280×800，滚动到列表中段，**When** 查看吸顶区，**Then** 只有一条吸顶栏：检索框 + 年份下拉 + 件数；高度 ≤ 72px（当前约 265px，占视口 1/3）
2. **Given** 任意滚动位置，**When** 观察吸顶栏上下边缘，**Then** 下层内容不透出（当前两层 sticky 之间有缝）
3. **Given** 手机端，**When** 滚动，**Then** 吸顶栏高度 ≤ 64px

**Notes**：桌面年份也改用下拉，与手机一致。

#### SUNA-16 · 有关键词时默认按相关度排序

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | Medium（P2） |
| Story Points | 5 |
| Labels | search, ranking |
| Blocked by | SUNA-13 |

**User Story**

> 作为**搜「伊達判決」的学生**，我想解说类、标题直接命中的文章排在前面，以便不用翻过十几篇诉讼旁听报告才找到入门文章。

**Acceptance Criteria**

1. **Given** q 非空，**When** 打开结果，**Then** 默认「関連度順」：标题命中 > 正文命中次数 > 发布日期新；有排序切换「関連度順 / 新しい順」
2. **Given** q=伊達判決，**When** 查看前 5 条，**Then** 至少 3 条为标题含「伊達判決」的文章
3. **Given** 关联度排序，**When** 查看列表，**Then** 隐藏年/月分组标题；每条显示年份
4. **Given** 任意排序，**When** 刷新或分享，**Then** URL 带 sort=relevance|date；q 为空时 sort 参数无效，按日期分组

**Notes**：纯前端计算，复用现有的全文索引。

#### SUNA-17 · 检索摘要中去掉原始 URL

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | Medium（P2） |
| Story Points | 1 |
| Labels | search, snippet |

**User Story**

> 作为**扫读检索结果的读者**，我想摘要里都是可读的句子，以便不被 https://youtu.be/… 之类的字符串打断。

**Acceptance Criteria**

1. **Given** q=伊達判決，**When** 查看全部 45 条摘要，**Then** 没有任何摘要包含 http:// 或 https://
2. **Given** 去掉 URL 后摘要过短，**When** 生成摘要，**Then** 向后多取文字补足，长度与现有摘要一致

#### SUNA-18 · URL 中无效的筛选值自动清理

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-3 |
| Priority | Low（P3） |
| Story Points | 1 |
| Labels | search, url |

**User Story**

> 作为**分享检索链接的读者**，我想链接里的条件和页面显示一致，以便别人打开时不会困惑。

**Acceptance Criteria**

1. **Given** 打开 ?q=伊達判決&type=guide&language=ja&year=2024（该组合 0 件），**When** 页面加载完成，**Then** year 回退为全部，同时 URL 通过 history.replaceState 去掉 year=2024
2. **Given** URL 中所有值都有效，**When** 页面加载，**Then** URL 不变

**Notes**：来自 9-27 审计 N9。

---

### SUNA-4 · Epic：浏览列表：从卡片墙改为可扫读的紧凑列表

* **Issue Type**：Epic
* **Labels**：ux, archive-list
* **Story 数 / Points**：1 / 5
* **背景**：浏览模式有 208 张卡片 + 75 个月份标题，手机整页 36,665px（45 屏）。

#### SUNA-19 · 浏览模式改为紧凑行列表

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-4 |
| Priority | Medium（P2） |
| Story Points | 5 |
| Labels | archive-list, mobile |

**User Story**

> 作为**想随便翻翻有什么文章的读者**，我想一屏能看到更多标题，以便能快速扫过 208 篇，找到感兴趣的。

**Acceptance Criteria**

1. **Given** q 为空（浏览模式），手机 375×812，**When** 查看列表，**Then** 每条 ≤ 64px 高：标题一行（超长省略）+ 日期 · 种类一行
2. **Given** 浏览模式，**When** 查看分组，**Then** 只保留年份标题；月份作为每条日期的一部分显示，不再单独占行（当前 75 个月份标题）
3. **Given** 手机 375×812，**When** 测量 archive.html 总高，**Then** ≤ 18,000px（当前 36,665px）
4. **Given** q 非空（检索模式），**When** 查看列表，**Then** 保持现有卡片 + 摘要 + 高亮样式

**Notes**：语言标签只在非日语文章上显示（91% 是日语，逐条显示「Japanese / 日本語」是噪音）。

---

### SUNA-5 · Epic：文章页：让从搜索引擎直接进来的读者知道身在何处

* **Issue Type**：Epic
* **Labels**：ux, article
* **Story 数 / Points**：3 / 5
* **背景**：文章页是外部流量的主要落地页。当前返回链接夹在两层导航之间；保存版性质只在页脚说明；手机正文列只有 297px。

#### SUNA-20 · 文章页返回链接改为标题上方的面包屑

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-5 |
| Priority | High（P1） |
| Story Points | 2 |
| Labels | article, nav |

**User Story**

> 作为**读完一篇想看同类文章的读者**，我想在标题上方看到这篇属于哪一年、哪一类，并能直接点过去，以便不用回到一览重新筛选。

**Acceptance Criteria**

1. **Given** 任意文章页，**When** 查看标题上方，**Then** 显示「記事一覧 › 2022年 › 解説」，三级均可点击
2. **Given** 点击「2022年」，**When** 跳转，**Then** archive.html?year=2022
3. **Given** 点击「解説」，**When** 跳转，**Then** archive.html?year=2022&type=guide
4. **Given** 从检索结果进入文章页，**When** 点击「記事一覧」，**Then** 回到进入前的检索状态（保留现有 q/type/language/year 回链行为）
5. **Given** 任意文章页，**When** 查看导航区，**Then** 原先夹在两层导航之间的「← アーカイブ一覧」移除
6. **Given** 屏幕阅读器，**When** 读到面包屑，**Then** 包在 nav aria-label="パンくず / Breadcrumb" 中，当前层级有 aria-current

#### SUNA-21 · 文章页标题旁加「保存版」徽章

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-5 |
| Priority | High（P1） |
| Story Points | 2 |
| Labels | article, trust |

**User Story**

> 作为**从 Google 直接进入文章页的读者**，我想一眼知道这是保存副本，而不是砂川平和ひろば的官网，以便不会把旧活动预告当成最新消息，也知道原页面在哪。

**Acceptance Criteria**

1. **Given** 全部 208 篇文章页，**When** 查看标题下的元信息行，**Then** 最前面显示徽章「保存版 · 2026-09-05取得」
2. **Given** 点击徽章，**When** 跳转，**Then** about.html 的来历说明小节（锚点）
3. **Given** 元信息行，**When** 查看，**Then** 「Original page / 元ページ」「引用形式をコピー」保留原位置
4. **Given** 深色 / 浅色，**When** 查看徽章，**Then** 文字与背景对比度 ≥ 4.5:1

**Notes**：徽章文案要与 SUNA-23 的授权说明保持一致。

#### SUNA-22 · 手机端正文加宽

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-5 |
| Priority | Medium（P2） |
| Story Points | 1 |
| Labels | article, mobile, readability |

**User Story**

> 作为**用手机读长文的读者**，我想每行多几个字，以便长文不用那么频繁地换行、滚动。

**Acceptance Criteria**

1. **Given** 视口 < 600px，**When** 打开任意文章页，**Then** 文章卡片去掉边框和内边距；正文宽度 ≥ 335px（当前 297px）
2. **Given** 视口 ≥ 600px，**When** 打开任意文章页，**Then** 保持现有卡片样式

---

### SUNA-6 · Epic：来历与授权：公开说明本档案的授权状态

* **Issue Type**：Epic
* **Labels**：content, trust
* **Story 数 / Points**：1 / 1
* **背景**：全站没有一处说明「是否取得砂川平和ひろば的同意」。这不是 UI 问题，但它阻塞门户层引入图片，且与 E5 的保存版徽章共用同一套说明。

#### SUNA-23 · 写明本档案的授权状态

| 字段 | 值 |
| -- | -- |
| Issue Type | Story |
| Parent (Epic) | SUNA-6 |
| Priority | Highest（P0） |
| Story Points | 1 |
| Labels | content, trust, decision-needed |

**User Story**

> 作为**砂川平和ひろば的关系者，或想引用本站的研究者**，我想知道这些文章是否经过ひろば同意才公开，以便能判断这个副本的地位，以及要不要联系谁。

**Acceptance Criteria**

1. **Given** about.html「砂川平和ひろばとの関係」小节末，**When** 阅读，**Then** 包含以下三种之一，并附日期：① 已取得了解（日期、形式）② 未取得正式许诺，权利人要求即撤下 ③ 正在联系中（联系日期）
2. **Given** 首页定位声明下方，**When** 阅读，**Then** 有一行与 about.html 一致的简短说明
3. **Given** changelog.html，**When** 查看更新履歴，**Then** 有一条记录此次追加

**Notes**：需要维护者先做决定，技术工作量极小。阻塞：门户层引入图片（不在本 PRD 范围）。

---

## 6. 发布计划

**Sprint 1 · 快速修复（约 1 天）** — 10 pts

* SUNA-23 写明本档案的授权状态（Highest · 1）
* SUNA-13 结果件数与「すべて解除」移到检索框正下方（Highest · 2）
* SUNA-10 首页正文里的ひろば邮箱改标签，避免发错对象（High · 1）
* SUNA-17 检索摘要中去掉原始 URL（Medium · 1）
* SUNA-20 文章页返回链接改为标题上方的面包屑（High · 2）
* SUNA-21 文章页标题旁加「保存版」徽章（High · 2）
* SUNA-11 定位声明降权，挪到简介段之后（Medium · 1）

**Sprint 2 · 手机与筛选（约 2 天）** — 15 pts

* SUNA-7 手机端导航收进「メニュー」按钮（Highest · 5）
* SUNA-8 主题切换压缩为单个图标按钮（High · 2）
* SUNA-9 首页直接放检索框，提交后跳转记事一览（High · 2）
* SUNA-14 筛选顺序改为 种类 → 年份 → 语言，语言组折叠（High · 3）
* SUNA-15 合并吸顶区为一条，修复两层吸顶间的文字透出（High · 3）

**Sprint 3 · 列表与排序（约 2 天）** — 13 pts

* SUNA-19 浏览模式改为紧凑行列表（Medium · 5）
* SUNA-16 有关键词时默认按相关度排序（Medium · 5）
* SUNA-22 手机端正文加宽（Medium · 1）
* SUNA-12 「砂川闘争年表」改为主题卡，替换「現地を歩く」（Medium · 1）
* SUNA-18 URL 中无效的筛选值自动清理（Low · 1）

排序原则：先做「改一行就能止损」的（发错邮箱、看不到反馈、授权说明），再做模板级改动（导航、吸顶），最后做需要调试的交互（排序、紧凑列表）。

## 7. Definition of Done（全部 Story 通用）

* 桌面 1280×800 与手机 375×812 实测通过全部验收标准，记录实测数值
* 浅色 / 深色两种主题下检查一遍
* 键盘可操作：Tab 顺序合理，焦点可见
* 现有 URL（含 `?q=&type=&language=&year=`）打开结果不变
* 站内链接 0 个 404（重跑全站链接检查）
* changelog.html 记录本次变更，**只写线上已验证的内容**

## 8. 待决问题

| \# | 问题 | 需要谁决定 | 影响 |
| -- | -- | -- | -- |
| Q1 | 授权状态选 ① / ② / ③ 中的哪一种 | 维护者 | SUNA-23、SUNA-21 的徽章文案 |
| Q2 | 手机菜单用全屏覆盖还是下拉展开 | 维护者 | SUNA-7 的实现方式，不影响验收 |
| Q3 | 关联度排序是否要给编辑页（入门、年表）加权 | 维护者 | SUNA-16 |
