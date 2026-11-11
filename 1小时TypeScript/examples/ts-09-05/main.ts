const input = document.querySelector("#amount");
if (input instanceof HTMLInputElement) {
  const amount = Number(input.value);
  if (Number.isFinite(amount)) {
    console.log(amount + 8);
  }
}

export {};
