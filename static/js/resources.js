// Resources app common JavaScript functionality
document.addEventListener("DOMContentLoaded", function () {
  // Like functionality
  const likeButtons = document.querySelectorAll(".like-button");
  likeButtons.forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const resourceId = this.dataset.resourceId;
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;

      fetch(`/resources/${resourceId}/like/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json",
        },
      })
        .then((response) => response.json())
        .then((data) => {
          const likesCount = document.getElementById(
            `likes-count-${resourceId}`
          );
          likesCount.textContent = data.likes_count;

          const heartIcon = this.querySelector("i");
          if (data.liked) {
            heartIcon.classList.remove("bi-heart");
            heartIcon.classList.add("bi-heart-fill");
          } else {
            heartIcon.classList.remove("bi-heart-fill");
            heartIcon.classList.add("bi-heart");
          }
        })
        .catch((error) => console.error("Error:", error));
    });
  });

  // File preview functionality
  const fileInput = document.getElementById("id_file");
  const filePreview = document.getElementById("filePreview");
  if (fileInput && filePreview) {
    fileInput.addEventListener("change", function () {
      filePreview.innerHTML = "";
      if (this.files && this.files[0]) {
        const file = this.files[0];
        if (file.type.startsWith("image/")) {
          const img = document.createElement("img");
          img.src = URL.createObjectURL(file);
          img.className = "img-fluid rounded";
          img.style.maxHeight = "300px";
          filePreview.appendChild(img);
        } else {
          const info = document.createElement("div");
          info.className = "alert alert-info";
          info.innerHTML = `Selected file: ${file.name} (${(
            file.size /
            1024 /
            1024
          ).toFixed(2)} MB)`;
          filePreview.appendChild(info);
        }
      }
    });
  }

  // Tags input enhancement
  const tagsInput = document.getElementById("id_tags");
  const tagPreview = document.getElementById("tagPreview");
  if (tagsInput && tagPreview) {
    function updateTagPreview() {
      const tags = tagsInput.value
        .split(",")
        .filter((tag) => tag.trim().length > 0);
      tagPreview.innerHTML = "";
      tags.forEach((tag) => {
        const badge = document.createElement("span");
        badge.className = "badge bg-info text-dark me-1 mb-1";
        badge.style.cursor = "pointer";
        badge.textContent = tag.trim();
        badge.onclick = function () {
          const newTags = tagsInput.value
            .split(",")
            .filter((t) => t.trim() !== tag.trim())
            .map((t) => t.trim())
            .join(", ");
          tagsInput.value = newTags;
          updateTagPreview();
        };
        tagPreview.appendChild(badge);
      });
    }

    tagsInput.addEventListener("input", updateTagPreview);
    updateTagPreview();
  }

  // Resource type dependent fields
  const resourceTypeSelect = document.getElementById("id_resource_type");
  const fileUploadSection = document.getElementById("fileUploadSection");
  const linkSection = document.getElementById("linkSection");
  if (resourceTypeSelect && fileUploadSection && linkSection) {
    function updateFieldVisibility() {
      const selectedType = resourceTypeSelect.value;
      if (selectedType === "link") {
        fileUploadSection.style.display = "none";
        linkSection.style.display = "block";
      } else {
        fileUploadSection.style.display = "block";
        linkSection.style.display = selectedType === "video" ? "block" : "none";
      }
    }

    resourceTypeSelect.addEventListener("change", updateFieldVisibility);
    updateFieldVisibility();
  }
});
