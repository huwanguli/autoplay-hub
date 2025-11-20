# AutoPlay Hub JSON 脚本规范 v2.1

本文档定义了 AutoPlay Hub 自动化脚本的JSON结构。v2.1版本在v2.0的基础上，为`action`节点增加了强大的`validate`（验证）块，使脚本具备了自我检查和修正的能力。

## 顶层结构

一个脚本是一个JSON对象，包含以下顶层键：

| 键 | 类型 | 是否必须 | 描述 |
| :--- | :--- | :--- | :--- |
| `version` | String | 是 | 脚本规范的版本，目前为 `"2.1"`。 |
| `name` | String | 是 | 脚本的名称。 |
| `description` | String | 否 | 对脚本功能的详细描述。 |
| `variables` | Object | 否 | 定义脚本中可以使用的变量键值对。 |
| `steps` | Array | 是 | 一个包含多个步骤节点的数组，脚本将按顺序执行这些步骤。 |

```json
{
  "version": "2.1",
  "name": "示例脚本",
  "description": "一个演示所有功能的脚本。",
  "variables": {
    "username": "testuser"
  },
  "steps": [
    // ... 步骤节点 ...
  ]
}
```

## 步骤节点 (Step Nodes)

`steps`数组中的每一个元素都是一个“步骤节点”对象。每个节点必须包含一个`type`字段。

### 类型 1: `action` - 动作节点

这是最核心的节点，用于执行一个具体的原子操作。

| 键 | 类型 | 是否必须 | 描述 |
| :--- | :--- | :--- | :--- |
| `type` | String | 是 | 固定为 `"action"`。 |
| `description`| String | 否 | 对此动作的描述，会显示在日志中。 |
| `action` | String | 是 | 要执行的具体动作名称，如 `touch`, `swipe`, `sleep`, `text` 等。 |
| `params` | Object | 是 | 一个包含动作所需参数的对象。 |
| `on_failure` | String/Object| 否 | 定义当动作本身失败时的策略（例如`touch`找不到图片）。默认为`"abort"`。 |
| `validate` | Object | 否 | **(v2.1新增)** 定义动作执行完毕后，用于验证结果的逻辑块。 |

---

### **v2.1 新增：`validate` 验证块**

`validate`块是一个可选的对象，用于断言一个动作执行后，界面是否达到了预期的状态。

**`validate` 对象的结构:**

| 键 | 类型 | 是否必须 | 描述 |
| :--- | :--- | :--- | :--- |
| `type` | String | 是 | 验证的类型。目前支持 `"image_exists"`。 |
| `target` | String | 是 | 期望在屏幕上存在的元素。对于`image_exists`，这是目标图片的**文件名**。 |
| `timeout`| Number | 否 | 验证的超时时间（秒）。在超时时间内，会持续检查条件是否满足。默认为 **5** 秒。|
| `on_failure` | String | 否 | 当在超时时间内**验证失败**时的策略。默认为 `"abort"`。 |

**`on_failure` 的可选值:**

*   `"abort"`: (默认值) 立即中止整个任务，并标记为失败。
*   `"retry_step"`: 重新执行**整个步骤**（包括`action`和`validate`）。为了防止无限重试，系统内置最多重试3次。
*   `"ignore"`: 忽略此次验证失败，继续执行下一个步骤。

#### **`action` 节点完整示例**

```json
{
  "type": "action",
  "description": "点击登录按钮，并验证是否跳转到了主页",
  "action": "touch",
  "params": {
    "target": "login_button.png"
  },
  "on_failure": {
    "retry": { "count": 2, "delay": 1 }
  },
  "validate": {
    "type": "image_exists",
    "target": "homepage_avatar.png",
    "timeout": 5,
    "on_failure": "retry_step"
  }
}
```
**执行逻辑解读:**
1.  尝试 `touch` "login_button.png"。
2.  如果找不到该图片，根据 `on_failure` 策略，会重试2次。如果最终还是失败，则中止任务。
3.  如果 `touch` 成功，则进入 `validate` 阶段。
4.  在接下来的5秒内，持续检查 "homepage_avatar.png" 是否出现在屏幕上。
5.  如果在5秒内出现，验证成功，此步骤结束。
6.  如果在5秒后仍未出现，根据 `validate` 的 `on_failure` 策略，执行 `retry_step`。
7.  `retry_step` 会让程序回到第1步，再次点击登录按钮，然后再次验证。这个过程最多重复3次。如果3次后依然验证失败，则中止整个任务。

---

### 类型 2: `loop` - 循环节点

用于重复执行一组步骤。

| 键 | 类型 | 是否必须 | 描述 |
| :--- | :--- | :--- | :--- |
| `type` | String | 是 | 固定为 `"loop"`。 |
| `loop_type`| String | 是 | 循环类型，目前支持 `"count"`。 |
| `count` | Number | 是 | 对于`count`类型，这是循环的次数。 |
| `steps` | Array | 是 | 一个包含多个步骤节点的数组，这些步骤将在每次循环中被执行。 |

```json
{
  "type": "loop",
  "loop_type": "count",
  "count": 3,
  "description": "向下连续滑动3次",
  "steps": [
    {
      "type": "action",
      "action": "swipe",
      "params": { "start": [500, 1500], "end": [500, 500] }
    },
    {
      "type": "action",
      "action": "sleep",
      "params": { "duration": 1 }
    }
  ]
}
```

### 类型 3: `condition` - 条件节点

用于根据条件执行不同的步骤分支。

| 键 | 类型 | 是否必须 | 描述 |
| :--- | :--- | :--- | :--- |
| `type` | String | 是 | 固定为 `"condition"`。 |
| `condition_type`| String| 是 | 条件类型，目前支持 `"if_image_exists"`。 |
| `params` | Object | 是 | 条件判断所需的参数，例如要检查的图片。|
| `if_true` | Array | 是 | 当条件为真时，要执行的步骤节点数组。 |
| `if_false` | Array | 否 | 当条件为假时，要执行的步骤节点数组。 |

```json
{
  "type": "condition",
  "condition_type": "if_image_exists",
  "description": "如果看到了更新提示，就点击'以后再说'",
  "params": {
    "target": "update_prompt.png"
  },
  "if_true": [
    {
      "type": "action",
      "action": "touch",
      "params": { "target": "later_button.png" }
    }
  ],
  "if_false": []
}
```