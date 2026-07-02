(() => {
  const form = document.querySelector("#exam-form");
  if (!form) return;
  const cards = [...document.querySelectorAll(".question-card")];
  const navButtons = [...document.querySelectorAll("[data-jump]")];
  const progressBar = document.querySelector("#progress-bar");
  const progressText = document.querySelector("#progress-text");
  const timer = document.querySelector("#timer");
  const modal = document.querySelector("#submit-modal");
  let current = 0;
  let seconds = Number(timer.dataset.seconds);

  const save = () => {
    const data = {};
    new FormData(form).forEach((value, key) => data[key] = value);
    localStorage.setItem("quizora-answers", JSON.stringify(data));
  };
  const restore = () => {
    const data = JSON.parse(localStorage.getItem("quizora-answers") || "{}");
    Object.entries(data).forEach(([name, value]) => {
      const input = form.querySelector(`[name="${name}"][value="${value}"]`);
      if (input) input.checked = true;
    });
  };
  const update = () => {
    const answered = cards.filter(card => card.querySelector("input:checked")).length;
    progressText.textContent = `${answered} / ${cards.length}`;
    progressBar.style.width = `${answered / cards.length * 100}%`;
    navButtons.forEach((button, index) => {
      button.classList.toggle("active", index === current);
      button.classList.toggle("answered", !!cards[index].querySelector("input:checked"));
    });
  };
  const show = index => {
    current = Math.max(0, Math.min(cards.length - 1, index));
    cards.forEach((card, i) => card.classList.toggle("hidden", i !== current));
    update();
    window.scrollTo({top: 0, behavior: "smooth"});
  };
  const openModal = () => {
    const answered = cards.filter(card => card.querySelector("input:checked")).length;
    document.querySelector("#modal-summary").textContent = `You answered ${answered} of ${cards.length} questions. This action cannot be undone.`;
    modal.classList.remove("hidden");
  };
  const submit = () => {
    localStorage.removeItem("quizora-answers");
    form.submit();
  };

  restore(); update();
  form.addEventListener("change", () => { save(); update(); });
  document.querySelectorAll(".next").forEach(button => button.addEventListener("click", () => show(current + 1)));
  document.querySelectorAll(".prev").forEach(button => button.addEventListener("click", () => show(current - 1)));
  navButtons.forEach(button => button.addEventListener("click", () => show(Number(button.dataset.jump))));
  document.querySelector(".submit-trigger").addEventListener("click", openModal);
  document.querySelector("#keep-reviewing").addEventListener("click", () => modal.classList.add("hidden"));
  document.querySelector("#confirm-submit").addEventListener("click", submit);

  const tick = () => {
    const minutes = String(Math.floor(seconds / 60)).padStart(2, "0");
    const remaining = String(seconds % 60).padStart(2, "0");
    timer.textContent = `${minutes}:${remaining}`;
    if (seconds <= 60) timer.parentElement.classList.add("warning");
    if (seconds-- <= 0) submit();
  };
  tick();
  setInterval(tick, 1000);
})();
