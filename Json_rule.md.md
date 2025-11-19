# AutoPlay Hub 脚本规范 v2.0

本文档定义了 AutoPlay Hub 自动化脚本的JSON文件结构和规则。一个脚本文件描述了一个完整的自动化任务流程。

## 1. 顶层结构

每个脚本文件都是一个JSON对象，包含以下顶层字段：

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `version` | String | 是 | 脚本规范的版本号，当前为 `"2.0"`。 |
| `name` | String | 是 | 脚本的可读名称，例如 `"微信每日签到"`。 |
| `description`| String | 否 | 对脚本功能的详细描述。 |
| `variables` | Object | 否 | 定义脚本级别的变量。键是变量名，值是默认值。在步骤参数中可通过 `{{variable_name}}` 语法引用。|
| `steps` | Array | 是 | 一个由“节点”（Node）对象组成的数组，定义了任务的执行流程。 |

**示例:**
```json
{
  "version": "2.0",
  "name": "登录并截图示例",
  "description": "一个演示登录流程并截图的示例脚本。",
  "variables": {
    "username": "default_user",
    "screenshot_name": "login_success.png"
  },
  "steps": [
    // ... 节点定义 ...
  ]
}
```

---

## 2. 节点 (Node)

`steps` 数组中的每个元素都是一个“节点”。所有节点共享一个通用结构，并根据 `type` 字段决定其具体行为和附加字段。

### 2.1 通用节点字段

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `type` | String | 是 | 节点类型。决定了节点的行为。有效值见下文。 |
| `description`| String | 否 | 对该步骤功能的用户友好描述，例如 `"输入用户名"`。 |

---

## 3. 核心节点类型

### 3.1 `type: "action"`

代表一个单一的、不可分割的原子操作。

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `action` | String | 是 | 要执行的原子动作的名称。 |
| `params` | Object | 否 | 一个包含动作所需参数的键值对对象。 |
| `on_failure` | String/Object | 否 | 定义当此动作失败时的处理策略。 |

#### `action` 的有效值:
*   `"touch"`: 点击屏幕上的一个位置。`params`: `{"target": "image.png"}`。
*   `"swipe"`: 从一个点滑动到另一个点。`params`: `{"start": [x1, y1], "end": [x2, y2]}`。
*   `"text"`: 输入文本。`params`: `{"text": "要输入的文字"}`。
*   `"sleep"`: 等待一段时间。`params`: `{"duration": 5}` (秒)。
*   `"snapshot"`: 截取当前屏幕。`params`: `{"filename": "my_screenshot.png"}`。

#### `on_failure` 的有效值:
*   `"abort"` (默认值): 立即中止整个任务，并标记为 `FAILED`。
*   `"ignore"`: 忽略错误，继续执行下一个节点。
*   `{"retry": {"count": N, "delay": D}}`: 当失败时，重试 `N` 次，每次重试之间间隔 `D` 秒。如果所有重试都失败，则中止任务。

**示例:**
```json
{
  "type": "action",
  "description": "点击登录按钮，如果找不到就重试3次",
  "action": "touch",
  "params": {
    "target": "login_button.png"
  },
  "on_failure": {
    "retry": {
      "count": 3,
      "delay": 2
    }
  }
}
```

### 3.2 `type: "loop"`

重复执行一系列子步骤。

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `loop_type` | String | 是 | 循环类型。当前仅支持 `"count"`。 |
| `count` | Integer | 是 | 当 `loop_type` 为 `"count"` 时，指定循环执行的次数。 |
| `steps` | Array | 是 | 一个包含子节点的数组，将在每次循环中被依次执行。 |

**示例:**
```json
{
  "type": "loop",
  "description": "连续向下滑动3次",
  "loop_type": "count",
  "count": 3,
  "steps": [
    { "type": "action", "action": "swipe", "params": {"start": [500, 1500], "end": [500, 500]} },
    { "type": "action", "action": "sleep", "params": {"duration": 1} }
  ]
}
```

### 3.3 `type: "condition"`

实现 "if...then...else" 逻辑分支。

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `condition_type` | String | 是 | 条件判断的类型。 |
| `params` | Object | 是 | 条件判断所需的参数。 |
| `if_true` | Array | 是 | 当条件为真时，执行此数组中的子节点。 |
| `if_false` | Array | 否 | 当条件为假时，执行此数组中的子节点。如果省略，则什么也不做。|

#### `condition_type` 的有效值:
*   `"if_image_exists"`: 检查指定图片是否存在于当前屏幕上。`params`: `{"target": "image.png"}`。

**示例:**
```json
{
  "type": "condition",
  "description": "如果有关闭按钮，就点击它",
  "condition_type": "if_image_exists",
  "params": {
    "target": "close_button.png"
  },
  "if_true": [
    {
      "type": "action",
      "action": "touch",
      "params": { "target": "close_button.png" }
    }
  ]
}
```

### 3.4 `type: "sub_script"`

执行一个预定义的、可复用的操作序列（也称为“函数”或“子程序”）。这些子程序在后端的 `airtest_runner.py` 中实现。

| 字段名 | 类型 | 必需 | 描述 |
| :--- | :--- | :--- | :--- |
| `name` | String | 是 | 要调用的子脚本的名称，例如 `"standard_login"`。 |
| `params` | Object | 否 | 传递给子脚本的参数。 |

**示例:**
```json
{
  "type": "sub_script",
  "description": "使用变量执行标准登录流程",
  "name": "standard_login",
  "params": {
    "username": "{{username}}",
    "password": "hardcoded_password"
  }
}
```

---

