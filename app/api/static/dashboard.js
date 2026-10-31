const metricsContainer = document.getElementById("metrics");
const statusBadge = document.getElementById("statusBadge");
const actionResult = document.getElementById("actionResult");
const videosTableBody = document.getElementById("videosTableBody");
const logsPanel = document.getElementById("logsPanel");
const uploadResult = document.getElementById("uploadResult");

const formatDate = (value) => (value ? new Date(value).toLocaleString() : "-");

async function api(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

function renderMetrics(status, uploads) {
  const counts = uploads.counts || {};
  const cards = [
    ["Agent Running", status.running ? "Yes" : "No"],
    ["Queued", counts.queued || 0],
    ["Uploaded", counts.uploaded || 0],
    ["Failed", counts.failed || 0],
    ["Total Videos", uploads.total || 0],
    ["Last Scan", status.last_scan_count || 0],
    ["Last Processed", status.last_processed_count || 0],
  ];

  metricsContainer.innerHTML = cards
    .map(
      ([label, value]) => `
      <div class="metric">
        <div class="label">${label}</div>
        <div class="value">${value}</div>
      </div>
    `,
    )
    .join("");

  statusBadge.textContent = status.running ? "Agent is running" : "Agent is stopped";
  statusBadge.classList.toggle("status-running", status.running);
  statusBadge.classList.toggle("status-stopped", !status.running);
}

function renderVideos(videos) {
  if (!videos.length) {
    videosTableBody.innerHTML = '<tr><td colspan="7" class="muted">No videos yet.</td></tr>';
    return;
  }

  videosTableBody.innerHTML = videos
    .map(
      (video) => `
      <tr>
        <td>${video.id}</td>
        <td>${video.file_name}</td>
        <td><span class="status-pill ${video.status}">${video.status}</span></td>
        <td>${video.title || "-"}</td>
        <td>${video.youtube_video_id || "-"}</td>
        <td title="${video.error_message || ""}">${video.error_message || "-"}</td>
        <td>${formatDate(video.created_at)}</td>
      </tr>
    `,
    )
    .join("");
}

async function refreshLogs() {
  const payload = await api("/logs?tail=100");
  logsPanel.textContent = payload.lines.length ? payload.lines.join("\n") : "No logs available yet.";
}

async function refreshDashboard() {
  const [status, uploads, videos] = await Promise.all([api("/status"), api("/uploads"), api("/videos")]);
  renderMetrics(status, uploads);
  renderVideos(videos);
}

async function runAction(action) {
  try {
    actionResult.textContent = "Processing...";
    if (action === "refresh") {
      await refreshDashboard();
      await refreshLogs();
      actionResult.textContent = "Dashboard refreshed.";
      return;
    }

    const payload = await api(`/actions/${action}`, { method: "POST" });
    await refreshDashboard();
    await refreshLogs();
    actionResult.textContent = `Action completed: ${JSON.stringify(payload)}`;
  } catch (error) {
    actionResult.textContent = error.message;
  }
}

async function uploadVideo(event) {
  event.preventDefault();
  const input = document.getElementById("videoFile");
  if (!input.files.length) {
    uploadResult.textContent = "Select a file first.";
    return;
  }

  const file = input.files[0];
  const formData = new FormData();
  formData.append("file", file);

  try {
    uploadResult.textContent = "Uploading...";
    const payload = await api("/upload", { method: "POST", body: formData });
    uploadResult.textContent = `Uploaded ${payload.file_name} to queue folder.`;
    input.value = "";
    await refreshDashboard();
  } catch (error) {
    uploadResult.textContent = error.message;
  }
}

document.querySelectorAll("[data-action]").forEach((button) => {
  button.addEventListener("click", () => runAction(button.dataset.action));
});

document.getElementById("uploadForm").addEventListener("submit", uploadVideo);
document.getElementById("refreshLogs").addEventListener("click", refreshLogs);

refreshDashboard().then(refreshLogs).catch((error) => {
  actionResult.textContent = error.message;
});
