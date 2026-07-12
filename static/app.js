const form = document.getElementById("registration-form");
const formSection = document.getElementById("form-section");
const paymentSection = document.getElementById("payment-section");
const successSection = document.getElementById("success-section");
const errorEl = document.getElementById("form-error");
const paymentErrorEl = document.getElementById("payment-error");
const submitBtn = document.getElementById("submit-btn");
const confirmPaymentBtn = document.getElementById("confirm-payment-btn");
const successMessage = document.getElementById("success-message");
const footerWhatsappLink = document.getElementById("footer-whatsapp-link");
const footerWhatsappNumber = document.getElementById("footer-whatsapp-number");
const successWhatsappLink = document.getElementById("success-whatsapp-link");
const successWhatsappNumber = document.getElementById("success-whatsapp-number");
const pricePreview = document.getElementById("price-preview");
const seatsSelect = form.querySelector('[name="seats"]');
const paymentAmount = document.getElementById("payment-amount");
const paymentBreakdown = document.getElementById("payment-breakdown");
const registrationIdEl = document.getElementById("registration-id");
const payUpiBtn = document.getElementById("pay-upi-btn");
const upiIdDisplay = document.getElementById("upi-id-display");
const copyUpiBtn = document.getElementById("copy-upi-btn");
const paymentQrDynamic = document.getElementById("payment-qr-dynamic");
const upiReferenceInput = document.getElementById("upi-reference");

let pricePerSeat = 3000;
let activeRegistrationId = null;

loadStatus();

seatsSelect.addEventListener("change", updatePricePreview);

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
  submitBtn.textContent = "Please wait…";

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

    showPaymentStep(result);
  } catch (err) {
    showError(err.message || "Could not continue to payment. Please try again.");
    submitBtn.disabled = false;
    submitBtn.textContent = "Continue to Payment";
  }
});

confirmPaymentBtn.addEventListener("click", async () => {
  paymentErrorEl.hidden = true;

  if (!activeRegistrationId) {
    showPaymentError("Registration reference missing. Please start again.");
    return;
  }

  const upiReference = upiReferenceInput.value.trim();
  if (!upiReference || upiReference.length < 8) {
    showPaymentError("Please enter your UPI transaction ID (UTR) from your payment app.");
    return;
  }

  confirmPaymentBtn.disabled = true;
  confirmPaymentBtn.textContent = "Submitting…";

  try {
    const response = await fetch("/api/confirm-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        registration_id: activeRegistrationId,
        upi_reference: upiReference,
      }),
    });

    const result = await response.json().catch(() => ({}));

    if (!response.ok) {
      const detail = result.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).join(" ")
        : detail || "Could not confirm payment. Please try again.";
      throw new Error(message);
    }

    successMessage.textContent = result.message;
    if (result.workshop_date) {
      const dateEl = document.getElementById("success-date");
      if (dateEl) dateEl.textContent = result.workshop_date;
    }
    if (result.venue) {
      const venueEl = document.getElementById("success-venue");
      if (venueEl) venueEl.textContent = result.venue;
    }
    if (result.maps_url) {
      const mapsEl = document.getElementById("success-maps-link");
      if (mapsEl) mapsEl.href = result.maps_url;
    }
    if (result.whatsapp_link && result.whatsapp_number) {
      applyWhatsappContact(result.whatsapp_link, result.whatsapp_number);
    }

    paymentSection.hidden = true;
    successSection.hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    showPaymentError(err.message || "Could not confirm payment. Please try again.");
    confirmPaymentBtn.disabled = false;
    confirmPaymentBtn.textContent = "Submit Payment Details";
  }
});

copyUpiBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(upiIdDisplay.textContent);
    copyUpiBtn.textContent = "Copied!";
    setTimeout(() => {
      copyUpiBtn.textContent = "Copy";
    }, 2000);
  } catch {
    copyUpiBtn.textContent = "Copy failed";
  }
});

async function loadStatus() {
  try {
    const response = await fetch("/api/status");
    const data = await response.json();
    if (data.price_per_seat) {
      pricePerSeat = Number(data.price_per_seat);
    }
    if (data.whatsapp_link && data.whatsapp_number) {
      applyWhatsappContact(data.whatsapp_link, data.whatsapp_number);
    }
    updatePricePreview();
  } catch {
    updatePricePreview();
  }
}

function updatePricePreview() {
  const seats = Number(seatsSelect.value);
  if (!seats) {
    pricePreview.hidden = true;
    return;
  }

  const total = pricePerSeat * seats;
  const fmt = (n) => n.toLocaleString("en-IN");
  pricePreview.textContent = `Total: ₹${fmt(total)} (${seats} × ₹${fmt(pricePerSeat)})`;
  pricePreview.hidden = false;
}

function showPaymentStep(result) {
  const payment = result.payment;
  activeRegistrationId = result.registration_id;

  paymentAmount.textContent = `₹${payment.amount_due.toLocaleString("en-IN")}`;
  paymentBreakdown.textContent =
    `${payment.seats} seat${payment.seats > 1 ? "s" : ""} × ₹${payment.price_per_seat.toLocaleString("en-IN")}`;
  registrationIdEl.textContent = result.registration_id;
  payUpiBtn.href = payment.upi_link;
  upiIdDisplay.textContent = payment.upi_id;
  paymentQrDynamic.src = payment.qr_image_url;

  formSection.hidden = true;
  paymentSection.hidden = false;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function applyWhatsappContact(link, number) {
  footerWhatsappLink.href = link;
  footerWhatsappNumber.textContent = number;
  successWhatsappLink.href = link;
  successWhatsappNumber.textContent = number;
}

function showError(message) {
  errorEl.textContent = message;
  errorEl.hidden = false;
}

function showPaymentError(message) {
  paymentErrorEl.textContent = message;
  paymentErrorEl.hidden = false;
}
