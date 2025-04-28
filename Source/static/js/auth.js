// Toggle password visibility
document.querySelector('.toggle-password').addEventListener('click', () => {
    const input = document.getElementById('password');
    input.type = input.type === 'password' ? 'text' : 'password';
  });