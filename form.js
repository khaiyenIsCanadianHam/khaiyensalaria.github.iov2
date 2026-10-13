/* Progressive enhancement for a static Web3Forms inquiry. No inquiry data is persisted. */
(() => {
  'use strict';

  const form = document.getElementById('inquiry-form');
  if (!form) return;

  const steps = Array.from(form.querySelectorAll('[data-step]'));
  const nextButton = form.querySelector('[data-form-next]');
  const previousButton = form.querySelector('[data-form-previous]');
  const submitButton = form.querySelector('[data-form-submit]');
  const submitLabel = submitButton.textContent.trim();
  const feedback = form.querySelector('[data-form-feedback]');
  const progress = form.querySelector('[data-form-progress]');
  const progressItems = Array.from(form.querySelectorAll('[data-progress-step]'));
  const stepStatus = form.querySelector('[data-step-status]');
  const review = form.querySelector('[data-review-summary]');
  const projectType = form.elements.namedItem('project_type');
  const conditionalGroups = Array.from(form.querySelectorAll('[data-project-type]'));
  const accessKey = form.elements.namedItem('access_key');
  const message = form.elements.namedItem('message');
  const email = 'khaiyenbusiness@gmail.com';
  let currentStep = 0;
  let submitting = false;

  const controlsFor = (container) => Array.from(container.querySelectorAll('input:not([type="hidden"]), select, textarea'));
  const selectedFeatures = () => Array.from(form.querySelectorAll('[name="requested_features"]:checked'), (input) => input.value);
  const keyConfigured = () => Boolean(accessKey.value.trim() && !accessKey.value.includes('YOUR_') && !accessKey.value.includes('[TODO'));

  function clearError(control) {
    control.removeAttribute('aria-invalid');
    const error = document.getElementById(`${control.id}-error`);
    if (error) {
      error.textContent = '';
      error.hidden = true;
    }
  }

  function errorFor(control) {
    if (control.disabled || !control.willValidate) return '';
    if (control.required && (control.type === 'checkbox' ? !control.checked : !control.value.trim())) {
      if (control.name === 'privacy_acknowledgment') return 'Please read and acknowledge the Privacy Notice before sending your inquiry.';
      if (control.tagName === 'SELECT') return 'Please select a project type.';
      if (control.name === 'message') return 'Please tell me a little about your project.';
      if (control.name === 'email') return 'Please enter your email address.';
      return 'Please enter your full name.';
    }
    if (control.validity.typeMismatch) return control.type === 'email' ? 'Please enter a valid email address, such as you@example.com.' : 'Please enter a complete website address, including https://.';
    if (control.validity.badInput || control.validity.rangeUnderflow || control.validity.rangeOverflow || control.validity.stepMismatch) return 'Please enter a whole number between 0 and 10,000,000.';
    if (control.maxLength > -1 && control.value.length > control.maxLength) return `Please use ${control.maxLength.toLocaleString()} characters or fewer.`;
    if (!control.validity.valid) return 'Please check this field before continuing.';
    return '';
  }

  function validateControl(control) {
    const errorText = errorFor(control);
    clearError(control);
    if (!errorText) return true;
    control.setAttribute('aria-invalid', 'true');
    const error = document.getElementById(`${control.id}-error`);
    if (error) {
      error.textContent = errorText;
      error.hidden = false;
    }
    return false;
  }

  function validateStep(index) {
    let firstInvalid = null;
    controlsFor(steps[index]).forEach((control) => {
      if (!validateControl(control) && !firstInvalid) firstInvalid = control;
    });
    return firstInvalid;
  }

  function syncConditionalFields() {
    conditionalGroups.forEach((group) => {
      const relevant = group.dataset.projectType === projectType.value;
      group.hidden = !relevant;
      controlsFor(group).forEach((control) => {
        // Disabled controls are excluded from FormData and constraint validation.
        // Values are kept in memory so returning to a category restores the draft.
        control.disabled = !relevant;
        if (!relevant) clearError(control);
      });
    });
  }

  function renderReview() {
    const rows = [];
    const alwaysShow = new Set(['name', 'email', 'project_type', 'project_goal', 'estimated_budget', 'timeline', 'message']);
    form.querySelectorAll('[data-review-label]').forEach((control) => {
      if (control.disabled || (!control.value && !alwaysShow.has(control.name))) return;
      const value = control.value || 'Not specified';
      rows.push([control.dataset.reviewLabel, value]);
      if (control.name === 'project_goal') rows.push(['Requested features', selectedFeatures().join(', ') || 'Not specified']);
    });
    const fragment = document.createDocumentFragment();
    rows.forEach(([label, value]) => {
      const row = document.createElement('div');
      const term = document.createElement('dt');
      const description = document.createElement('dd');
      term.textContent = label;
      description.textContent = value;
      row.append(term, description);
      fragment.append(row);
    });
    // Only text nodes are created from visitor-entered values.
    review.replaceChildren(fragment);
  }

  function showStep(index, moveFocus = true) {
    currentStep = index;
    steps.forEach((step, stepIndex) => { step.hidden = stepIndex !== index; });
    progressItems.forEach((item, stepIndex) => {
      item.classList.toggle('is-complete', stepIndex < index);
      if (stepIndex === index) item.setAttribute('aria-current', 'step');
      else item.removeAttribute('aria-current');
    });
    stepStatus.textContent = `Step ${index + 1} of ${steps.length} · ${steps[index].dataset.stepTitle}`;
    previousButton.hidden = index === 0;
    nextButton.hidden = index === steps.length - 1;
    submitButton.hidden = index !== steps.length - 1;
    if (index === steps.length - 1) renderReview();
    if (moveFocus) steps[index].querySelector('legend').focus();
  }

  function setFeedback(text, state, moveFocus = false, offerEmail = false) {
    feedback.replaceChildren(document.createTextNode(text));
    feedback.dataset.state = state;
    if (offerEmail) {
      const link = document.createElement('a');
      link.href = `mailto:${email}`;
      link.textContent = email;
      feedback.append(document.createTextNode(' You can also email '), link, document.createTextNode('.'));
    }
    if (moveFocus) feedback.focus();
  }

  function continueToNextStep() {
    if (submitting) return;
    const invalid = validateStep(currentStep);
    if (invalid) {
      invalid.focus();
      return;
    }
    setFeedback('', 'idle');
    showStep(Math.min(currentStep + 1, steps.length - 1));
  }

  function updateMessageCount() {
    form.querySelector('#inquiry-message-count').textContent = `${message.value.length.toLocaleString()} / 5,000`;
  }

  function setSubmitting(active) {
    submitting = active;
    form.setAttribute('aria-busy', String(active));
    steps.forEach((step) => { step.disabled = active; });
    [nextButton, previousButton, submitButton].forEach((button) => { button.disabled = active; });
    submitButton.textContent = active ? 'Sending your inquiry…' : submitLabel;
  }

  nextButton.addEventListener('click', continueToNextStep);
  previousButton.addEventListener('click', () => {
    if (!submitting) showStep(Math.max(0, currentStep - 1));
  });
  projectType.addEventListener('change', syncConditionalFields);
  message.addEventListener('input', updateMessageCount);
  form.addEventListener('input', (event) => {
    if (event.target.matches('[aria-invalid="true"]')) validateControl(event.target);
  });
  form.addEventListener('change', (event) => {
    if (event.target.matches('[aria-invalid="true"]')) validateControl(event.target);
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (submitting) return;
    if (currentStep < steps.length - 1) {
      continueToNextStep();
      return;
    }

    for (let index = 0; index < steps.length; index += 1) {
      const invalid = validateStep(index);
      if (invalid) {
        showStep(index, false);
        invalid.focus();
        return;
      }
    }

    if (!keyConfigured()) {
      setFeedback('Online submission is not available yet. Your details are still here; please contact me directly to discuss your project.', 'error', true, true);
      return;
    }
    if (form.elements.namedItem('botcheck').checked) {
      setFeedback('Your inquiry could not be submitted. Please contact me directly.', 'error', true, true);
      return;
    }

    const formData = new FormData(form);
    // Replace all repeated checkbox entries with exactly one readable field.
    formData.delete('requested_features');
    formData.set('requested_features', selectedFeatures().join(', ') || 'Not specified');
    const payload = Object.fromEntries(formData.entries());
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 20000);
    setSubmitting(true);
    setFeedback('Sending your project inquiry. Please keep this page open.', 'pending');

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
        credentials: 'omit',
        referrerPolicy: 'no-referrer'
      });
      let result;
      try {
        result = await response.json();
      } catch {
        throw new Error('invalid-response');
      }
      if (!response.ok || result?.success !== true) throw new Error('submission-rejected');

      // Clear values only after the provider explicitly confirms success.
      form.reset();
      controlsFor(form).forEach(clearError);
      syncConditionalFields();
      updateMessageCount();
      showStep(0, false);
      setFeedback("Your project inquiry has been submitted successfully. Thank you for your interest. I'll review your details and respond using the email address you provided.", 'success', true);
    } catch (error) {
      const text = error.name === 'AbortError'
        ? 'The request timed out, so I could not confirm delivery. Your details are still here. Before retrying, please note that the original inquiry may have reached me.'
        : 'I could not confirm that your inquiry was submitted. Your details are still here. Please try again or contact me directly.';
      setFeedback(text, 'error', true, true);
    } finally {
      window.clearTimeout(timeout);
      setSubmitting(false);
    }
  });

  // Enhance only after handlers are ready; native POST remains the no-JS fallback.
  form.noValidate = true;
  form.classList.add('is-enhanced');
  progress.hidden = false;
  review.hidden = false;
  form.querySelector('[data-review-intro]').hidden = false;
  form.querySelector('[data-form-availability]').hidden = keyConfigured();
  syncConditionalFields();
  updateMessageCount();
  showStep(0, false);
})();
