let lastPrompt = "";

function setRuntimeStatus(backend, modelId, device) {
  document.getElementById("statusBackend").textContent = backend || "-";
  document.getElementById("statusModelId").textContent = modelId || "-";
  document.getElementById("statusDevice").textContent = device || "-";
}

async function generate() {
  const description = document.getElementById("description").value.trim();
  if (!description) {
    alert("请输入描述");
    return;
  }

  setRuntimeStatus("生成中...", "生成中...", "生成中...");

  try {
    const res = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description })
    });

    const raw = await res.text();
    let data = {};
    try {
      data = raw ? JSON.parse(raw) : {};
    } catch {
      data = { error: raw || "后端返回了非JSON响应" };
    }

    if (!res.ok) {
      setRuntimeStatus(data.backend || "生成失败", data.model_id, data.device);
      alert(data.error || `生成失败（HTTP ${res.status}）`);
      return;
    }

    if (!data.image) {
      alert("生成成功但未返回图片数据");
      setRuntimeStatus(data.backend, data.model_id, data.device);
      return;
    }

    lastPrompt = data.enhanced_prompt || "";
    document.getElementById("promptBox").textContent = data.enhanced_prompt || "";
    document.getElementById("sourceBox").textContent = (data.sources || []).join(", ");
    document.getElementById("preview").src = "data:image/png;base64," + data.image;
    setRuntimeStatus(data.backend, data.model_id, data.device);
  } catch (err) {
    setRuntimeStatus("请求失败", "-", "-");
    alert("请求失败: " + (err?.message || err));
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/history?limit=10");
    const data = await res.json();
    const root = document.getElementById("history");
    root.innerHTML = "";
    for (const item of data.items || []) {
      const div = document.createElement("div");
      div.className = "history-item";
      div.innerHTML = `<div><strong>描述:</strong> ${item.description}</div>
        <div><strong>Prompt:</strong> ${item.enhanced_prompt}</div>
        <img src="data:image/png;base64,${item.image}" alt="history"/>`;
      root.appendChild(div);
    }
  } catch (err) {
    alert("加载历史失败: " + (err?.message || err));
  }
}

async function vote(v) {
  if (!lastPrompt) {
    alert("请先生成一张图");
    return;
  }
  await fetch("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enhanced_prompt: lastPrompt, vote: v })
  });
}

document.getElementById("generateBtn").addEventListener("click", generate);
document.getElementById("loadHistoryBtn").addEventListener("click", loadHistory);
document.getElementById("likeBtn").addEventListener("click", () => vote("up"));
document.getElementById("dislikeBtn").addEventListener("click", () => vote("down"));
