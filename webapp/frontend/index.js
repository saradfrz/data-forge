const form = document.getElementById('purchaseForm');
const result = document.getElementById('result');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = {
    code: document.getElementById('code').value,
    description: document.getElementById('description').value,
    quantity: parseFloat(document.getElementById('quantity').value),
    unit_price: parseFloat(document.getElementById('unit_price').value)
  };

  try {
    const res = await fetch('/api/purchase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    const text = await res.text();
    result.innerText = text;
    form.reset();
  } catch (err) {
    result.innerText = 'Error submitting data';
    console.error(err);
  }
});
