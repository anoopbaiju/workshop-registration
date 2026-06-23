const form = document.getElementById("registration-form");
const formSection = document.getElementById("form-section");
const successSection = document.getElementById("success-section");
const errorEl = document.getElementById("form-error");
const submitBtn = document.getElementById("submit-btn");
const earlyBirdSlots = document.getElementById("early-bird-slots");
const successMessage = document.getElementById("success-message");
const footerWhatsappLink = document.getElementById("footer-whatsapp-link");
const footerWhatsappNumber = document.getElementById("footer-whatsapp-number");
const successWhatsappLink = document.getElementById("success-whatsapp-link");
const successWhatsappNumber = document.getElementById("success-whatsapp-number");

loadStatus();

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorEl.hidden = true;

  const data = Object.fromEntries(new FormData(form).entries());

  if (!data.full_name?.trim() || !data.whatsapp?.trim() || !data.email?.trim()) {
    showError("Please fill in all required fields.");
    return;
  }

  if (!data.age_group || !data.seats) {
    showError("Please select age group and number of seats.");
    return;
  }

  if (data.source === "") delete data.source;
  if (data.message === "") delete data.message;

  submitBtn.disabled = true;
  submitBtn.textContent = "Submitting…";

  try {
    const response = await fetch("/api/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...data,
        seats: Number(data.seats),
      }),
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail = result.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).join(" ")
        : detail || "Something went wrong. Please try again.";
      throw new Error(message);
    }

    successMessage.textContent = result.message;
    if (result.whatsapp_link && result.whatsapp_number) {
      applyWhatsappContact(result.whatsapp_link, result.whatsapp_number);
    }
    formSection.hidden = true;
    successSection.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    showError(err.message || "Could not submit registration. Please try again.");
    submitBtn.disabled = false;
    updateSubmitLabel(Number(earlyBirdSlots.dataset.remaining ?? 0));
  }
});

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    updateEarlyBirdBanner(data.early_bird_remaining ?? 10);
    if (data.whatsapp_link && data.whatsapp_number) {
      applyWhatsappContact(data.whatsapp_link, data.whatsapp_number);
    }
  } catch {
    earlyBirdSlots.textContent = "Early bird offer — limited seats";
  }
}

function applyWhatsappContact(link, number) {
  footerWhatsappLink.href = link;
  footerWhatsappNumber.textContent = number;
  successWhatsappLink.href = link;
  successWhatsappNumber.textContent = number;
}

function updateEarlyBirdBanner(remaining) {
  earlyBirdSlots.dataset.remaining = String(remaining);

  if (remaining <= 0) {
    earlyBirdSlots.textContent = "Early bird slots are full — standard pricing applies";
    earlyBirdSlots.classList.add("sold-out");
    submitBtn.textContent = "Book Your Seat Now";
    submitBtn.classList.add("standard-offer");
    return;
  }

  if (remaining === 1) {
    earlyBirdSlots.textContent = "Only 1 early bird slot left!";
  } else {
    earlyBirdSlots.textContent = `${remaining} early bird slots remaining`;
  }

  updateSubmitLabel(remaining);
}

function updateSubmitLabel(remaining) {
  if (remaining <= 0) {
    submitBtn.textContent = "Book Your Seat Now";
    submitBtn.classList.add("standard-offer");
  } else {
    submitBtn.textContent = "Avail Early Bird Offer — Book Now";
    submitBtn.classList.remove("standard-offer");
  }
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
}
