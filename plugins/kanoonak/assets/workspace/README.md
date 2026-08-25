---
kanoonak: readme                  # علامة نوع الملف — دليل مساحة العمل
convention: 2026-07-21            # نسخة اتفاقية المجلد
---

# قانونك — دليل مساحة العمل / The Kanoonak workspace guide

النص العربي في هذا الدليل هو النص المعتمد؛ الترجمة الإنجليزية شرح مساعد لا غير.
*The Arabic text of this guide is authoritative; the English gloss is an aid only.*

## 1. ما هذا المجلد — What this folder is

هذا المجلد هو السجل المحلي المعتمد للقضايا على جهاز القاضي. وعندما يطلب القاضي من مضيف الذكاء الاصطناعي العمل على ملف، قد يعالج المضيف محتواه وفق حساب القاضي وضوابط البيانات لديه. ولا تتلقى أداة قانونك المحلية بيانات اعتماد حساب قانونك، ولا ترسل مسار المجلد أو إذن الوصول إليه أو محتويات ملفاته إلى خدمة MCP البعيدة لقانونك. أما تسليمات التصوير البعيدة، إن استُخدمت، فتخضع لسياسة الاحتفاظ المنفصلة الخاصة بها.

> **Gloss (EN):** This folder is the canonical local matter record on the judge's device. When the judge asks the AI host to work on a file, the host may process its content under the judge's account and data controls. The local Kanoonak helper receives no Kanoonak account credential and sends no folder path, access grant, or file content to Kanoonak's remote MCP service. Remote capture deliveries, if used, remain subject to their separate retention policy.

من يكتب فيه ثلاثة: **مساعد الذكاء الاصطناعي** بأدوات ملفاته وبموجب توجيهات المنصة؛ و**تسليمات التصوير** التي تصل إلى مجلد «الوارد» بفعل المستخدم؛ و**القاضي** نفسه، ويده هي العليا دائماً. الالتزام بقواعد هذا الدليل واجب توجيهي على المساعد — لا يفرضه النظام فرضاً آلياً؛ ومخالفته تظهر للقاضي كفجوة مبلغ عنها في تقرير التدقيق، والتصرف فيها له وحده.

> **Gloss (EN):** Three writers exist: the AI assistant (via its file tools, under the platform's directives), capture deliveries arriving into the inbox at the user's action, and the judge himself, whose hand always prevails. The assistant's adherence is a directive-level duty, not machine-enforced; deviations surface as reported gaps for the judge to dispose of.

## 2. خريطة المجلد — Layout map

الاسم الافتراضي لمساحة العمل الجديدة هو `Kanoonak`، ويبقى الاسم `قانونك` مدعوماً لمساحات العمل القديمة أو المخصصة.

مساحة العمل:

```
Kanoonak/
|-- README.md            (هذا الدليل)
|-- الفهرس.md            (سجل القضايا — جدول واحد، صف لكل قضية)
|-- أسلوبي.md            (الشخصية المحلية — تفضيلات القاضي فوق التوجيه الأم)
\-- <مجلد لكل قضية>      (بقواعد التسمية في البند 3)
```

داخل كل قضية — عشرة عناصر تنشأ عند فتح القضية (إنشاء عند الغياب، لا كتابة فوق موجود):

```
استئناف-N-لسنة-YYق/
|-- الملخص.md            (ملخص القضية — المفتاح والخصوم والطلبات والنصاب والجلسات)
|-- المواعيد.md          (المواعيد — وأقربها القادم إلزامي الإثبات)
|-- الوارد/              (تسليمات التصوير الخام — دفعات لا تمس ولا تحذف)
|-- الحكم-المستأنف/      (حكم أول درجة — المدخل الأول في كل مهمة)
|-- الصحف/               (صحف الاستئناف وأسبابه — صحيفة لكل عضو)
|-- المذكرات/            (المذكرات والحوافظ — مجلد لكل خصم باسمه المثبت بالملخص)
|-- تقارير-الخبرة/       (تقارير الخبراء)
|-- اللائحة/             (لائحة نظام العاملين بالشركة — موضع تحقق الاستشهاد بها)
|-- المسودات/            (مسودات المساعد — مسودة-* فقط)
\-- الأحكام/             (النصوص الصادرة — نهائي أو معدل فقط)
```

> **Gloss (EN):** `Kanoonak` is the default name for a new workspace; `قانونك` remains supported for a legacy or custom workspace. The root holds this guide, the case registry (الفهرس), the local persona file (أسلوبي), and one folder per matter. Every matter bootstraps with exactly ten items — the summary and deadlines files plus eight slot folders (inbox, appealed judgment, petitions, memoranda, expert reports, company regulation, drafts, issued rulings) — created if absent, never overwritten.

## 3. قواعد التسمية — Naming grammar

اسم مجلد القضية هو إسقاط مفتاح القضية (النوع، الرقم، السنة، نوع السنة) على نظام الملفات: تسقط كلمة «رقم»، وتحل الشرطات محل المسافات، وتلصق «ق» بسنة قضائية من رقمين، والأرقام غربية دائماً (0-9)، والتواريخ في أسماء الملفات بصيغة YYYY-MM-DD:

| صورة القضية | صيغة الاسم | مثال | Gloss (EN) |
|---|---|---|---|
| استئناف واحد | استئناف-N-لسنة-YYق | استئناف-5214-لسنة-82ق | single appeal |
| استئنافات مضمومة بسنة واحدة | استئناف-N-و-M-لسنة-YYق | استئناف-5620-و-5771-لسنة-82ق | consolidated, same judicial year |
| استئنافات مضمومة بسنتين | استئناف-N-لسنة-YYق-و-M-لسنة-ZZق | استئناف-5310-لسنة-81ق-و-5488-لسنة-82ق | consolidated, cross-year |
| التماس إعادة النظر | التماس-N-لسنة-YYق | التماس-17-لسنة-82ق | iltimas petition |

- ترتيب الأعضاء في الأسماء المضمومة: الأصلي أولاً ثم المنضم فالفرعي فالضمني، تصاعدياً بالرقم داخل كل صفة، والأعضاء المتتالون بسنة واحدة يجمعون تحت «لسنة-YYق» واحدة.
- عنصر المحكمة في المفتاح يستكمل من «الفهرس.md» (مساحة العمل لدائرة واحدة)، والملخص يحمل المفتاح كاملاً.
- عند ضم لاحق يعاد تسمية مجلد الأصلي بالصيغة المضمومة وتنقل محتويات مجلد الشقيق إليه ولا يبقى في مجلد الشقيق إلا ملف «مضموم.md» يدل على المجلد الجامع؛ ولا يجرى الضم إلا بتعليمات القاضي.
- كل جزء اسم حر الاختيار (أسماء مجلدات الخصوم، أسماء مستندات الحوافظ) حروف عربية وأرقام غربية وشرطات فقط، لا مسافات، وبطول لا يجاوز عشرين حرفاً استحساناً.
- الأسماء كلها بترميز NFC؛ وقراءة الأسماء تتسامح مع اختلاف الترميز على القرص وتطبعه قبل المطابقة.

> **Gloss (EN):** A case-folder name is the filesystem projection of the case key: «رقم» dropped, hyphens for spaces, «ق» attached to the 2-digit judicial year, Western digits, ISO dates in names. Consolidated names order members أصلي then منضم then فرعي then ضمني, grouping consecutive same-year members under one «لسنة-YYق». The forum comes from الفهرس.md; الملخص.md holds the full key. Mid-stream consolidation renames the original's folder, moves the sibling's contents in, and leaves a single مضموم.md pointer — on the judge's instruction only. Free-choice segments: Arabic letters, Western digits, hyphens; no spaces; at most 20 characters recommended. All names are NFC.

## 4. علامات نوع الملف ومفاتيح البيانات — File-kind markers and front-matter keys

كل ملف منظم يفتتح بكتلة YAML أول مفاتيحها `kanoonak:` وقيمتها إحدى العلامات الاثنتي عشرة:

`matter-summary` (ملخص قضية) ، `deadlines` (مواعيد) ، `local-persona` (شخصية محلية) ، `index` (فهرس) ، `document` (مستند مقيد) ، `page` (صفحة واردة) ، `delivery-manifest` (بيان تسليم) ، `draft` (مسودة) ، `ruling` (حكم صادر) ، `bundle-list` (قائمة حافظة) ، `merged-pointer` (دليل ضم) ، `readme` (هذا الدليل)

مفاتيح البيانات إنجليزية لتنضبط المطابقة الآلية، وقيمها عربية، وكل مفتاح يكتب المساعد بجواره شرحاً عربياً عند التوليد:

| المفتاح | الشرح العربي | Gloss (EN) |
|---|---|---|
| kanoonak | علامة نوع الملف | file-kind marker |
| convention | نسخة اتفاقية المجلد | convention version |
| case | مفتاح القضية (النوع والرقم والسنة ونوعها والمحكمة) | the case key tuple |
| type | نوع القضية | case type |
| number | رقم القضية | case number |
| judicial_year | السنة القضائية (مع year_type: قضائية) | judicial year (2-digit) |
| year | السنة الميلادية (مع year_type: ميلادية) | Gregorian year (4-digit) |
| year_type | نوع السنة | year type |
| forum | المحكمة | forum |
| appeals | الاستئنافات الأعضاء | member appeals |
| role | صفة العضو | member role |
| first_instance | بيانات حكم أول درجة | first-instance data |
| outcome | منطوق أول درجة موجزاً | first-instance outcome |
| date | التاريخ | date |
| petition_target | الحكم الملتمس فيه | the challenged ruling (التماس) |
| parties | الخصوم | parties |
| name | الاسم كما بالأوراق | party name as in the record |
| folder | اسم مجلد الخصم بالمذكرات | the party's pinned folder slug |
| capacity | الصفة | capacity |
| first_instance_role | المركز أمام أول درجة | first-instance role |
| appeal_roles | المركز في كل استئناف عضو | per-appeal roles |
| claims | الطلبات | claims |
| id | معرف ثابت | stable id |
| text | نص الطلب | claim text |
| amount | المبلغ بالجنيه أو null لغير النقدي | amount (null if non-monetary) |
| appeal | العضو الذي طرح به الطلب | pleading member appeal |
| valuation | بيانات النصاب | valuation |
| total | قيمة الدعوى يوم رفعها أو غير-مقدرة | total value at filing, or the literal |
| per_appeal | القيمة لكل عضو | per-member totals |
| basis | أساس التقدير | valuation basis |
| posture | الموقف الإجرائي الراهن | current posture |
| sessions | سجل الجلسات | session log |
| note | ملاحظة حرة | free note |
| status | حالة القضية | matter status |
| updated | تاريخ آخر صيانة | last maintenance date |
| next_deadline | أقرب ميعاد قادم أو لا-مواعيد | earliest open deadline, or the literal |
| next_deadline_id | معرف قيد الميعاد الأقرب | id of that entry |
| entries | قيود المواعيد | deadline entries |
| kind | نوع الميعاد أو نوع المحرر | entry kind / drafted-document kind |
| source | مصدر الإيداع أو منشئ الميعاد | source pointer |
| doc_type | نوع المستند | document type |
| party | الخصم المقدم أو null | submitting party slug, or null |
| received | تاريخ الإيداع | date received/filed |
| title | عنوان المستند | document title |
| batch | معرف الدفعة | delivery-batch id |
| delivered | وقت التسليم | delivery timestamp |
| pages | صفحات الدفعة | delivered pages |
| n | رقم الصفحة في البيان | page number in the manifest |
| page | رقم الصفحة | page number |
| captured | تاريخ الالتقاط | capture date |
| ocr | مصدر التعرف الضوئي | OCR source |
| state | حالة المحرر | lifecycle state |
| based_on | النسخة السابقة من المسودة | prior draft version |
| supersedes | النسخة السابقة من الحكم المعدل | the superseded issued file |
| session | جلسة النطق | pronouncement session |
| subject | موضوع الحكم التمهيدي | interlocutory subject |
| directive_version | نسخة التوجيه الأم المنتجة للمسودة | producing directive version |
| local_persona_updated | تاريخ ملف أسلوبي المعتمد | consumed أسلوبي update date |
| parent_version | نسخة التوجيه الأم آخر ما روجعت عليه | last reconciled parent version |
| merged_into | المجلد الجامع وعضو هذا الدليل | merge target (folder + member) |
| member | صورة عضو هذا الدليل | this pointer's member tuple |
| id_map | جدول تحويل معرفات المواعيد عند الضم | old-to-new deadline-id map |
| renames | جدول إعادة التسمية عند الضم | rename record |

> **Gloss (EN):** Every structured file opens with YAML front-matter whose first key is the ASCII marker `kanoonak:` (twelve values above). Keys are English for exact machine matching; values are Arabic; the assistant writes an Arabic gloss comment beside each key on generation.

## 5. جدول المفردات القانونية — Canonical vocabulary table

القيم الآتية هي الصور المعتمدة حرفاً بحرف (ترميز NFC، صيغة مذكرة واحدة للأدوار، شرطات لا مسافات):

| الفئة | القيم المعتمدة | Gloss (EN) |
|---|---|---|
| جذر مساحة العمل | Kanoonak (الافتراضي) ، قانونك (قديم أو مخصص) | workspace root (default; legacy/custom) |
| ملفات مساحة العمل | README.md ، الفهرس.md ، أسلوبي.md | workspace files |
| ملفا القضية الإلزاميان | الملخص.md ، المواعيد.md | the two mandatory files |
| مجلدات القضية الثمانية | الوارد ، الحكم-المستأنف ، الصحف ، المذكرات ، تقارير-الخبرة ، اللائحة ، المسودات ، الأحكام | the eight slot folders |
| ملفات بنيوية | تسليم.yaml ، قائمة.md ، مضموم.md | structural files |
| مفردات قواعد التسمية | استئناف ، التماس ، لسنة ، و ، ق | name-grammar vocabulary |
| بادئات أسماء الملفات المؤرخة | دفعة- ، صفحة- ، صحيفة- ، مذكرة- ، حافظة- ، مستند- ، تقرير- ، مسودة- ، حكم- ، حكم-تمهيدي- ، قرار- | dated name-class prefixes |
| أسماء خاصة | الحكم-المستأنف.md ، صحيفة-الالتماس.md ، لائحة-<اسم-المجلد>.md ، مستند-NN-<وصف>.md ، عقد-العمل (وصف محجوز لمستند عقد العمل) | special names incl. the reserved عقد-العمل slug |
| لاحقة التعديل | -معدل ، -معدل-2 ، -معدل-3 | amendment suffix chain |
| نوع القضية (type) | استئناف ، التماس | case type |
| نوع السنة (year_type) | قضائية ، ميلادية | year type |
| صفة العضو (role) | أصلي ، منضم ، فرعي ، ضمني ، التماس | member role |
| الصفة (capacity) | عامل ، صاحب-عمل ، أخرى | party capacity |
| المركز أمام أول درجة (first_instance_role) | مدعي ، مدعى-عليه | first-instance role |
| المركز الاستئنافي (appeal_roles) | مستأنف ، مستأنف-ضده ، ملتمس ، ملتمس-ضده | appellate roles |
| حالة القضية (status) | منظورة ، محجوزة-للحكم ، محكومة ، مشطوبة ، مضمومة | matter status |
| حالة المحرر (state) | مسودة ، نهائي ، معدل | lifecycle state |
| نوع المحرر (kind) | حكم ، حكم-تمهيدي ، قرار | drafted-document kind |
| موضوع التمهيدي (subject) | ندب-خبير ، استجواب | interlocutory subject |
| نوع الميعاد (kind بالمواعيد) | جلسة ، تقرير-خبير ، ميعاد-طعن ، تجديد ، أخرى | deadline kind |
| حالة الميعاد (status بالمواعيد) | قادم ، تم ، ملغي | deadline status |
| نوع المستند (doc_type) | صحيفة ، مذكرة ، مستند ، حكم-أول-درجة ، تقرير-خبير ، لائحة | document type |
| قيم حرفية معتمدة | لا-مواعيد ، غير-مقدرة ، يدوي | pinned literals |
| عناوين متن الملخص | الوقائع ، المسار الإجرائي ، ملاحظات | الملخص body headings |
| أعمدة الفهرس | المجلد ، الحالة ، الموعد القادم ، ملاحظة | الفهرس columns |
| علامة الفراغ | ⟦…⟧ | the placeholder token |

> **Gloss (EN):** These are the byte-exact canonical NFC spellings of every pinned name and enum value: workspace names, the ten bootstrap items, structural files, the naming-grammar vocabulary, dated name-class prefixes, special names (including the reserved عقد-العمل bundle-document slug), and every enum (roles in masculine canonical form, hyphenated, no spaces), plus the pinned literals and the placeholder token.

## 6. دورة المسودة والحكم — The draft/issued lifecycle

للمحررات ثلاث حالات ظاهرة في اسم الملف وفي حقل `state` معاً: **مسودة** (في «المسودات» وباسم يبدأ بمسودة-) ثم **نهائي** (في «الأحكام» باسم مؤرخ بجلسة النطق) ثم — عند التعديل بعد الإصدار — **معدل** (ملف جديد بلاحقة -معدل يجاور النسخة السابقة ويشير إليها بحقل `supersedes`، ولا تحذف نسخة سابقة أبداً).

المواضع التي تترك للقلم (كيوم الجلسة القادمة) تكتب في المسودات بعلامة الفراغ **⟦…⟧** — علامة لا تلتبس بنص قانوني؛ وورودها في ملف نهائي أو معدل فجوة يبلغ عنها التدقيق.

**هذه المخرجات كلها مسودات معروضة على القاضي: لا ينقل ملف من «المسودات» إلى «الأحكام» ولا يعد شيء صادراً إلا بتعليمات صريحة من القاضي؛ المساعد يقترح ويصوغ ولا يصدر حكماً.**

> **Gloss (EN):** Three lifecycle states, visible in both filename and `state` field: مسودة (draft, in المسودات with the مسودة- prefix), then نهائي (issued, in الأحكام, dated by pronouncement session), then معدل (post-issuance amendment: a new -معدل file beside the retained original, pointing at it via `supersedes`; predecessors are never deleted). Clerk-fill slots are written in drafts as the ⟦…⟧ placeholder token; its presence in any issued or amended file is a reported gap. The standing rule: all these outputs are drafts presented to the judge — nothing moves from drafts to issued rulings and nothing counts as issued except on the judge's explicit instruction; the AI proposes and drafts, and never issues.

## 7. قواعد الصيانة والتدقيق — Housekeeping invariants (H1–H17)

يدقق المساعد هذه القواعد عند كل مراجعة ويبلغ عن الفجوات تقريراً؛ ولا يصلح ولا ينقل ولا يحذف شيئاً من مادة القاضي إلا بتعليماته:

1. **H1** — كل اسم مجلد قضية يقرأ على قواعد التسمية (البند 3) إلى مفتاح قضية صحيح.
2. **H2** — كل مجلد قضية يحوي «الملخص.md» و«المواعيد.md» ببيانات أولها علامة النوع وكل الحقول الإلزامية مستوفاة غير فارغة، ومنها رقم الدعوى الابتدائية لكل عضو، ولكل خصم صفته ومركزه أمام أول درجة ومركزه في كل استئناف عضو.
3. **H3** — مفتاح اسم المجلد يطابق مفتاح الملخص وأعضاءه.
4. **H4** — كل مجلد فرعي في «المذكرات» يطابق اسم خصم مثبتاً بالملخص.
5. **H5** — كل مستند مقيد يفتتح بكتلة هوية؛ وقضيته من أعضاء القضية (لا من petition_target — فذلك دليل خطأ تقييد)، وخصمه — إن ذكر — من خصوم الملخص. الملفات البنيوية وصور الصفحات معفاة.
6. **H6** — «next_deadline» يساوي تاريخ أقرب قيد «قادم» (أو «لا-مواعيد» ولا قيد مفتوح)، و«next_deadline_id» يدل على قيده، و«updated» مثبت.
7. **H7** — حكم تمهيدي بموضوع «ندب-خبير» في «الأحكام» يستتبع قيد «تقرير-خبير» في المواعيد، وميعاد الإيداع قبل أول جلسة تالية بأسبوعين على الأقل.
8. **H8** — لا ملف بحالة «مسودة» أو باسم يبدأ بمسودة- في «الأحكام»، ولا ملف بغير ذلك في «المسودات».
9. **H9** — لا علامة فراغ ⟦…⟧ في ملف «نهائي» أو «معدل».
10. **H10** — كل ملف «معدل» يدل حقل «supersedes» فيه على نسخة سابقة قائمة بجواره، والسلسلة متصلة.
11. **H11** — في «الفهرس.md» صف واحد لكل مجلد قضية، وخانتا الحالة والموعد القادم تطابقان ملفات المجلد.
12. **H12** — إن استشهدت مسودة أو حكم بلائحة شركة وجب وجود ملف اللائحة باسم صاحبها في مجلد «اللائحة» — وإلا أبلغ عن الفجوة.
13. **H13** — كل ملف أو مجلد لا يطابق اسماً معتمداً يدرج في قائمة تعرض على القاضي، والتصرف فيه له وحده.
14. **H14** — اتساق التواريخ: الجلسات لا تسبق أحكام أول درجة، وجلسة كل حكم صادر من سجل جلسات الملخص، وتواريخ المواعيد لا تسبق تواريخ مصادرها.
15. **H15** — مجلد الضم لا يحوي إلا «مضموم.md» صحيحاً يدل على مجلد جامع قائم، وصفه في الفهرس بحالة «مضمومة».
16. **H16** — ملفات مساحة العمل الثلاثة قائمة ببياناتها، وكل مجلد قضية غير مضموم يحوي العناصر العشرة كاملة، وجدول المفردات في هذا الدليل تام مطابق للصور المعتمدة.
17. **H17** — كل «تسليم.yaml» ذكرت قضيته يطابق مجلده، ودفعة مجهولة القضية لا تكتب في مجلد قضية قبل تثبت المساعد من القاضي.

> **Gloss (EN):** The housekeeping audit checks: parseable folder names (H1); complete mandatory front-matter in الملخص/المواعيد incl. per-member first-instance numbers and per-party role data (H2); folder-name/summary key agreement (H3); memoranda subfolders matching party slugs (H4); identity blocks on filed documents with member-tuple and known-party checks (H5); next-deadline synchronization (H6); expert-referral entails a report-deadline entry with the two-week rule (H7); draft/issued separation (H8); no placeholder tokens in issued files (H9); intact supersedes chains (H10); registry agreement (H11); cited-لائحة presence (H12); unclassified items listed for the judge (H13); date coherence (H14); merged-pointer legitimacy (H15); workspace integrity incl. the ten-item set and this vocabulary table (H16); delivery-manifest/case agreement and no unconfirmed null-case batches (H17). The audit reports gaps; it never repairs, moves, or deletes without the judge's instruction.

## 8. نسخة الاتفاقية — Convention version

نسخة هذه الاتفاقية: **2026-07-21**، وهي المثبتة في حقل `convention:` بكل ملف منظم. مرجعها الموثق: `docs/prds/2026-07-21-case-folder-convention.md` في مستودع المنصة، وكل تعديل لاحق يصدر ملفاً مؤرخاً جديداً لا تعديلاً في موضعه.

> **Gloss (EN):** Convention version 2026-07-21, stamped in every structured file's `convention:` field. Documented lineage: `docs/prds/2026-07-21-case-folder-convention.md` in the platform repository; revisions are new dated files, never in-place edits.
