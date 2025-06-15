const signInBtnLink = document.querySelector('.signInBtn-link');
const signUpBtnLink = document.querySelector('.signUpBtn-link');
const wrapper = document.querySelector('.wrapper');

if (signUpBtnLink && wrapper) {
    signUpBtnLink.addEventListener('click', () => {
        wrapper.classList.toggle('active');
    });
}
if (signInBtnLink && wrapper) {
    signInBtnLink.addEventListener('click', () => {
        wrapper.classList.toggle('active');
    });
}
function togglePassword(fieldId, eyeIcon) {
    var field = document.getElementById(fieldId);
    if (field.type === "password") {
        field.type = "text";
        eyeIcon.textContent = '🙈';
    } else {
        field.type = "password";
        eyeIcon.textContent = '👁️';
    }
}