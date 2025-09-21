const $ = (sel) => document.querySelector(sel);

let sessionId = null;
let stream = null;
let videoEnabled = false;
let currentAudio = null;
let voiceEnabled = true;
let recognition = null;
let isListening = false;
let currentInputMode = 'text'; // 'text' or 'voice'

// Video capture functions
async function startVideo() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        width: { ideal: 640 }, 
        height: { ideal: 480 },
        facingMode: 'user'
      }, 
      audio: false 
    });
    
    const video = $('#video');
    video.srcObject = stream;
    videoEnabled = true;
    
    $('#video-status').textContent = 'Camera On';
    $('#video-status').classList.add('active');
    $('#toggle-video').textContent = 'Disable Camera';
    
    // Start periodic frame capture for analysis
    setInterval(captureFrame, 2000); // Capture every 2 seconds
    
  } catch (err) {
    console.error('Error accessing camera:', err);
    alert('Unable to access camera. Please check permissions.');
  }
}

function stopVideo() {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  
  videoEnabled = false;
  $('#video-status').textContent = 'Camera Off';
  $('#video-status').classList.remove('active');
  $('#toggle-video').textContent = 'Enable Camera';
}

function captureFrame() {
  if (!videoEnabled || !stream) return null;
  
  const video = $('#video');
  const canvas = $('#canvas');
  const ctx = canvas.getContext('2d');
  
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  ctx.drawImage(video, 0, 0);
  
  return canvas.toDataURL('image/jpeg', 0.8);
}

async function startInterview() {
  const role = $('#role').value.trim();
  const seniority = $('#seniority').value.trim();
  const preferredLanguage = $('#programming-language').value;
  if (!role || !seniority) return alert('Please enter role and seniority.');
  
  voiceEnabled = $('#enable-voice').checked;
  
  const res = await fetch('/api/session/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, seniority, preferred_language: preferredLanguage })
  });
  const data = await res.json();
  sessionId = data.session_id;
  $('#question').textContent = data.question;
  $('#setup').classList.add('hidden');
  $('#interview').classList.remove('hidden');
  $('#feedback').textContent = '';
  $('#video-feedback').textContent = '';
  $('#answer').value = '';
  $('#answer').focus();
  
  // Initialize speech recognition
  initSpeechRecognition();
  
  // Set default input mode
  setInputMode('text');
  
  // Auto-play the first question if voice is enabled
  if (voiceEnabled && data.audio_data) {
    setTimeout(() => playAudio(data.audio_data), 500); // Small delay to ensure UI is ready
  }
}

async function submitAnswer() {
  const answer = $('#answer').value.trim();
  const codeSolution = $('#code-editor').value.trim();
  if (!sessionId) return;
  if (!answer && !codeSolution) return alert('Please provide an answer or code solution.');
  
  // Capture current frame for analysis
  const videoFrame = captureFrame();
  
  const res = await fetch('/api/session/answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      session_id: sessionId, 
      answer,
      video_frame: videoFrame,
      code_solution: codeSolution || null
    })
  });
  const data = await res.json();
  
  // Display text feedback
  $('#feedback').textContent = `Feedback: ${data.feedback} (Score: ${data.score.toFixed(1)}/10)`;
  
  // Display video analysis feedback
  if (data.video_analysis) {
    displayVideoFeedback(data.video_analysis);
  }
  
  // Handle coding question
  if (data.coding_question) {
    displayCodingQuestion(data.coding_question);
  }
  
  // Display coding feedback
  if (data.coding_response) {
    displayCodingFeedback(data.coding_response);
  }
  
  if (data.finished) {
    $('#interview').classList.add('hidden');
    const s = data.summary;
    let summaryHtml = `
      <h2>Interview Summary</h2>
      <p><strong>Average Score:</strong> ${s.average_score}/10 over ${s.total_questions} questions</p>
      <p><strong>Strengths:</strong> ${(s.strengths || []).join(', ') || '—'}</p>
      <p><strong>Improvements:</strong> ${(s.improvements || []).join(', ') || '—'}</p>
      <p>${s.overall_feedback}</p>
    `;
    
    // Add video analysis summary if available
    if (data.video_analysis) {
      const va = data.video_analysis;
      summaryHtml += `
        <h3>Video Analysis Summary</h3>
        <div class="video-metrics">
          <div class="metric">
            <div class="metric-label">Eye Contact</div>
            <div class="metric-value ${getScoreClass(va.eye_contact.score)}">${va.eye_contact.score.toFixed(1)}/10</div>
          </div>
          <div class="metric">
            <div class="metric-label">Posture</div>
            <div class="metric-value ${getScoreClass(va.posture.score)}">${va.posture.score.toFixed(1)}/10</div>
          </div>
          <div class="metric">
            <div class="metric-label">Expressions</div>
            <div class="metric-value ${getScoreClass(va.facial_expressions.score)}">${va.facial_expressions.score.toFixed(1)}/10</div>
          </div>
          <div class="metric">
            <div class="metric-label">Gestures</div>
            <div class="metric-value ${getScoreClass(va.hand_gestures.score)}">${va.hand_gestures.score.toFixed(1)}/10</div>
          </div>
        </div>
      `;
    }
    
    summaryHtml += `<button onclick="location.reload()">Start New Session</button>`;
    $('#summary').innerHTML = summaryHtml;
    $('#summary').classList.remove('hidden');
    
    // Stop video when interview ends
    stopVideo();
  } else {
    $('#question').textContent = data.next_question;
    $('#answer').value = '';
    $('#answer').focus();
    
    // Auto-play the next question if voice is enabled
    if (voiceEnabled && data.audio_data) {
      setTimeout(() => playAudio(data.audio_data), 500); // Small delay to ensure UI is ready
    }
  }
}

function displayVideoFeedback(analysis) {
  const feedback = $('#video-feedback');
  let html = '<strong>Video Analysis:</strong><br>';
  
  html += `👁️ <strong>Eye Contact:</strong> ${analysis.eye_contact.feedback}<br>`;
  html += `🧍 <strong>Posture:</strong> ${analysis.posture.feedback}<br>`;
  html += `😊 <strong>Expressions:</strong> ${analysis.facial_expressions.feedback}<br>`;
  html += `✋ <strong>Gestures:</strong> ${analysis.hand_gestures.feedback}`;
  
  feedback.innerHTML = html;
}

function getScoreClass(score) {
  if (score >= 7) return '';
  if (score >= 5) return 'warning';
  return 'danger';
}

// Audio functions
function playAudio(audioData) {
  if (!audioData) {
    console.log("No audio data, trying browser TTS...");
    tryBrowserTTS();
    return;
  }
  
  // Stop current audio if playing
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  
  try {
    currentAudio = new Audio(audioData);
    currentAudio.playbackRate = parseFloat($('#voice-speed').value);
    
    currentAudio.addEventListener('play', () => {
      $('#play-question').classList.add('hidden');
      $('#pause-audio').classList.remove('hidden');
      $('#auto-play-status').classList.add('hidden');
    });
    
    currentAudio.addEventListener('pause', () => {
      $('#play-question').classList.remove('hidden');
      $('#pause-audio').classList.add('hidden');
      $('#auto-play-status').classList.add('hidden');
    });
    
    currentAudio.addEventListener('ended', () => {
      $('#play-question').classList.remove('hidden');
      $('#pause-audio').classList.add('hidden');
      $('#auto-play-status').classList.add('hidden');
      currentAudio = null;
    });
    
    // Auto-play when audio is ready
    currentAudio.addEventListener('canplaythrough', () => {
      currentAudio.play().catch(e => {
        console.error('Auto-play failed:', e);
        // Show play button if auto-play fails (browser restrictions)
        $('#play-question').classList.remove('hidden');
        $('#pause-audio').classList.add('hidden');
        $('#auto-play-status').classList.add('hidden');
      });
    });
    
    // Try immediate play, but don't show error if it fails (browser restrictions)
    currentAudio.play().catch(e => {
      console.log('Immediate play blocked by browser, will auto-play when ready');
    });
  } catch (e) {
    console.error('Audio creation error:', e);
  }
}

function pauseAudio() {
  if (currentAudio) {
    currentAudio.pause();
  }
}

function toggleAudioPlayback() {
  if (currentAudio) {
    if (currentAudio.paused) {
      currentAudio.play();
    } else {
      currentAudio.pause();
    }
  } else {
    // Try browser TTS if no audio data
    tryBrowserTTS();
  }
}

// Browser TTS fallback
function tryBrowserTTS() {
  const question = $('#question').textContent;
  if (!question) return;
  
  if ('speechSynthesis' in window) {
    console.log("Using browser TTS...");
    
    // Stop any current speech
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(question);
    utterance.rate = parseFloat($('#voice-speed').value);
    utterance.volume = 0.8;
    
    // Try to find a good voice
    const voices = speechSynthesis.getVoices();
    if (voices.length > 0) {
      // Prefer female voice
      const femaleVoice = voices.find(v => 
        v.name.toLowerCase().includes('female') || 
        v.name.toLowerCase().includes('zira') ||
        v.name.toLowerCase().includes('samantha')
      );
      if (femaleVoice) {
        utterance.voice = femaleVoice;
      } else {
        utterance.voice = voices[0];
      }
    }
    
    utterance.onstart = () => {
      $('#play-question').classList.add('hidden');
      $('#pause-audio').classList.remove('hidden');
      $('#auto-play-status').classList.add('hidden');
    };
    
    utterance.onend = () => {
      $('#play-question').classList.remove('hidden');
      $('#pause-audio').classList.add('hidden');
      $('#auto-play-status').classList.add('hidden');
    };
    
    utterance.onerror = (e) => {
      console.error('Browser TTS error:', e);
      $('#play-question').classList.remove('hidden');
      $('#pause-audio').classList.add('hidden');
      $('#auto-play-status').classList.add('hidden');
    };
    
    speechSynthesis.speak(utterance);
  } else {
    console.log("Browser TTS not supported");
    $('#play-question').classList.remove('hidden');
    $('#pause-audio').classList.add('hidden');
    $('#auto-play-status').classList.add('hidden');
  }
}

// Speech Recognition Functions
function initSpeechRecognition() {
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    recognition.onstart = () => {
      console.log('Speech recognition started');
      isListening = true;
      updateVoiceStatus('listening', '🎤 Listening... Speak now');
      $('#voice-input-btn').textContent = '⏹️ Stop Listening';
    };
    
    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      
      if (finalTranscript) {
        $('#answer').value = finalTranscript;
        updateVoiceStatus('success', '✅ Voice input received');
        setTimeout(() => {
          updateVoiceStatus('', '');
        }, 2000);
      } else if (interimTranscript) {
        updateVoiceStatus('listening', `🎤 Listening... "${interimTranscript}"`);
      }
    };
    
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      isListening = false;
      $('#voice-input-btn').textContent = '🎤 Voice Input';
      
      let errorMessage = 'Voice input error';
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not found. Please check your microphone.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone access denied. Please allow microphone access.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          break;
      }
      
      updateVoiceStatus('error', `❌ ${errorMessage}`);
      setTimeout(() => {
        updateVoiceStatus('', '');
      }, 3000);
    };
    
    recognition.onend = () => {
      console.log('Speech recognition ended');
      isListening = false;
      $('#voice-input-btn').textContent = '🎤 Voice Input';
      if (!isListening) {
        updateVoiceStatus('', '');
      }
    };
    
    console.log('Speech recognition initialized');
  } else {
    console.log('Speech recognition not supported');
    $('#voice-input-btn').style.display = 'none';
  }
}

function startVoiceInput() {
  if (!recognition) {
    updateVoiceStatus('error', '❌ Speech recognition not supported in this browser');
    return;
  }
  
  if (isListening) {
    stopVoiceInput();
    return;
  }
  
  try {
    recognition.start();
  } catch (e) {
    console.error('Error starting speech recognition:', e);
    updateVoiceStatus('error', '❌ Failed to start voice input');
  }
}

function stopVoiceInput() {
  if (recognition && isListening) {
    recognition.stop();
  }
}

function setInputMode(mode) {
  currentInputMode = mode;
  
  if (mode === 'voice') {
    $('#voice-input-btn').classList.add('active');
    $('#text-input-btn').classList.remove('active');
    $('#answer').placeholder = 'Click "Voice Input" to speak your answer...';
  } else {
    $('#voice-input-btn').classList.remove('active');
    $('#text-input-btn').classList.add('active');
    $('#answer').placeholder = 'Type your answer or use voice input...';
  }
}

function updateVoiceStatus(type, message) {
  const status = $('#voice-status');
  status.className = `voice-status ${type}`;
  status.textContent = message;
}

// Coding question functions
function displayCodingQuestion(question) {
  $('#coding-section').classList.remove('hidden');
  $('#input-section').classList.add('hidden');
  
  // Update problem statement
  $('#problem-text').textContent = question.problem_statement;
  
  // Update examples
  $('#examples-text').textContent = question.examples.join('\n\n');
  
  // Update constraints
  $('#constraints-text').textContent = question.constraints.join('\n');
  
  // Update difficulty and category badges
  const difficultyBadge = $('#coding-difficulty');
  difficultyBadge.textContent = question.difficulty.toUpperCase();
  difficultyBadge.className = `difficulty-badge ${question.difficulty}`;
  
  $('#coding-category').textContent = question.category.replace('_', ' ').toUpperCase();
  
  // Clear previous code
  $('#code-editor').value = '';
  
  // Set language based on preference
  const preferredLang = $('#programming-language').value;
  if (preferredLang) {
    $('#code-language').value = preferredLang;
  }
  
  // Focus on code editor
  $('#code-editor').focus();
}

function displayCodingFeedback(response) {
  const feedbackDiv = $('#coding-feedback');
  feedbackDiv.classList.remove('hidden');
  
  let html = `
    <h4>💻 Code Assessment Results</h4>
    <p><strong>Score:</strong> ${response.score.toFixed(1)}/10</p>
    <p><strong>Test Cases:</strong> ${response.test_cases_passed}/${response.total_test_cases} passed</p>
    <p><strong>Feedback:</strong> ${response.feedback}</p>
  `;
  
  if (response.time_complexity || response.space_complexity) {
    html += '<div class="complexity-info">';
    if (response.time_complexity) {
      html += `<div class="complexity-item">Time: ${response.time_complexity}</div>`;
    }
    if (response.space_complexity) {
      html += `<div class="complexity-item">Space: ${response.space_complexity}</div>`;
    }
    html += '</div>';
  }
  
  if (response.suggestions && response.suggestions.length > 0) {
    html += '<div class="suggestions">';
    html += '<h5>Suggestions for improvement:</h5>';
    html += '<ul>';
    response.suggestions.forEach(suggestion => {
      html += `<li>${suggestion}</li>`;
    });
    html += '</ul></div>';
  }
  
  feedbackDiv.innerHTML = html;
  
  // Hide coding section and show input section again
  setTimeout(() => {
    $('#coding-section').classList.add('hidden');
    $('#input-section').classList.remove('hidden');
    $('#answer').value = '';
    $('#answer').focus();
  }, 5000); // Auto-hide after 5 seconds
}

function runCode() {
  const code = $('#code-editor').value.trim();
  if (!code) {
    alert('Please write some code first.');
    return;
  }
  
  // Simple syntax highlighting simulation
  console.log('Running code:', code);
  alert('Code execution simulation - in a real implementation, this would run your code safely.');
}

function submitCode() {
  const code = $('#code-editor').value.trim();
  if (!code) {
    alert('Please write your solution before submitting.');
    return;
  }
  
  // Submit the code solution
  submitAnswer();
}

// Event listeners
$('#start').addEventListener('click', startInterview);
$('#submit').addEventListener('click', submitAnswer);
$('#toggle-video').addEventListener('click', () => {
  if (videoEnabled) {
    stopVideo();
  } else {
    startVideo();
  }
});

$('#play-question').addEventListener('click', toggleAudioPlayback);
$('#pause-audio').addEventListener('click', toggleAudioPlayback);

$('#voice-speed').addEventListener('input', (e) => {
  if (currentAudio) {
    currentAudio.playbackRate = parseFloat(e.target.value);
  }
});

// Voice input event listeners
$('#voice-input-btn').addEventListener('click', startVoiceInput);
$('#text-input-btn').addEventListener('click', () => setInputMode('text'));

// Coding event listeners
$('#run-code').addEventListener('click', runCode);
$('#submit-code').addEventListener('click', submitCode);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    submitAnswer();
  }
  
  // Space bar to toggle voice input
  if (e.code === 'Space' && e.ctrlKey && currentInputMode === 'voice') {
    e.preventDefault();
    startVoiceInput();
  }
});

// Initialize video when page loads
document.addEventListener('DOMContentLoaded', () => {
  // Auto-start video when interview starts
  $('#start').addEventListener('click', () => {
    setTimeout(() => {
      if (!videoEnabled) {
        startVideo();
      }
    }, 1000);
  });
});


