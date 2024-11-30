<template>
  <div class="main">
    <!-- First slide container for the first set of search engines -->
    <div class="slide_container">
      <div class="slide_name">
        <!-- Update the span to reflect the selected engine by adding 'active' class -->
        <span :class="{ active: selected === 1 }">Google</span>
        <span :class="{ active: selected === 3 }">DuckDuckGo</span>
        <span :class="{ active: selected === 4 }">Bing</span>
        <span :class="{ active: selected === 5 }">Brave</span>
      </div>
      <!-- Range slider bound to 'selected' -->
      <input type="range" min="1" max="4" v-model="selected" class="slider" id="myRange">
    </div>
    <div class="slide_container">
      <div class="slide_name">
        <!-- Update the span to reflect the selected engine by adding 'active' class -->
        <span :class="{ active: selected === 1 }">Google Scholar</span>
        <span :class="{ active: selected === 2 }">Pub Med</span>
      </div>
      <!-- Range slider bound to 'selected' -->
      <input type="range" min="1" max="2" v-model="selected2" class="slider" id="myRange2">
    </div>
    <!-- Second slide container for the second set of search engines -->
    <div class="slide_container">
      <div class="slide_name">
        <!-- Update the span to reflect the selected engine by adding 'active2' class -->
        <span :class="{ active2: selected2 === 1 }">Gemini</span>
        <span :class="{ active2: selected2 === 2 }">Pegasus+Gemini</span>
        <span :class="{ active2: selected2 === 3 }">T5</span>
        <span :class="{ active2: selected2 === 4 }">BART+Gemini</span>
      </div>
      <!-- Range slider bound to 'selected2' -->
      <input type="range" min="1" max="4" v-model="selected3" class="slider" id="myRange3">
    </div>
    <div class="answer_container">
      <div class="columns">
        <div class = "column left">
          <div v-if="answer">
            <h5>Answer</h5>
            <div v-html="answer" class="answer"></div>
          </div>

        </div>
        <div v-if="source.length > 0" class = "column right">
          <h5>Sources</h5>
          <ul class="source-list">
            <li v-for="(url, index) in source" :key="index">
              <a :href="url" target="_blank" rel="noopener noreferrer">{{ getDomain(url) }}</a>
            </li>
          </ul>
        </div>
        <div class = "column left">
          <div v-if="ai_answer" class = "ai_answer">
            <h5>AI</h5>
            <div v-html="ai_answer" class="ai-answer"></div>
          </div>
          <p v-else>Wait answer...</p>
        </div>
        <div v-if="doc_links.length > 0" class = "column right">
          <h5>Studies links</h5>
          <ul class="source-list">
            <li v-for="(url, index) in doc_links" :key="index">
              <a :href="url" target="_blank" rel="noopener noreferrer">{{ getDomain(url) }}</a>
            </li>
          </ul>
        </div>
      </div>
        <!-- Placeholder text before getting a real answer -->

    </div>
    <!-- Textarea for user input and a send button -->
    <div class="chat-input-container">
      <div class="chat-input-wrapper">
        <textarea name="message" class="chat-input" v-model="question" placeholder="Enter your question"></textarea>
        <button class="send-button" @click="sendQuestion">
          <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
            <path d="M2.01 21l20.99-9L2.01 3 2 10l15 2-15 2z"/>
          </svg>
        </button>
        </div>
    </div>
    <footer> </footer>
  </div>
</template>

<script>
import axios from 'axios' // Importing axios for HTTP requests
import { marked } from 'marked'
export default {
  data() {
    return {
      question: '',   // Holds the user question input
      answer: '',     // Holds the backend response
      source: '',
      ai_answer: '',
      doc_links: '',
      selected: 1,    // Value of the first search engine slider
      selected2: 1,   // Value of the second search engine slider
      selected3: 1,
    }
  },
  methods: {

    getDomain(url) {
      try {
        return new URL(url).hostname.replace('www.', '');
      } catch (error) {
        return url; // Fallback if URL parsing fails
      }
    },
    // Function to send the question to the backend
    sendQuestion() {
      axios.post('http://20.123.47.146:8080/api/check', {
        question: this.question,
        searchEngine: this.selected,
        db: this.selected2,
        aiEngine: this.selected3

      })
      .then(response => {
        console.log('Response from server:', response.data);
        this.answer = marked.parse(response.data.answer);
        this.source = response.data.source;
        this.ai_answer = marked.parse(response.data.ai_answer);
        this.doc_links = response.data.doc_links;
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }

  }
}
</script>

<style scoped>

.main{
  font-family: DM Sans,sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}

/* Style for the slider container */
.slide_container {
  width: 100%;
  text-align: center;
}

/* Style for the slider labels (search engine names) */
.slide_name {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
}

/* Style for each individual label */
.slide_name span {
  width: 20%;
  text-align: center;
}

/* Active class for the first slider */
.active {
  font-weight: bold;
}

/* Active class for the second slider */
.active2 {
  font-weight: bold;
}

/* Style for the range slider */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 80%;
  height: 25px;
  background: #d3d3d3;
  outline: none;
  opacity: 0.7;
  transition: opacity .2s;
  border-radius: 10px;
}

/* Style for the slider hover effect */
.slider:hover {
  opacity: 1;
}

/* Style for the slider thumb */
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 15%;
  height: 25px;
  background: #074a7d;
  cursor: pointer;
  border-radius: 10px;
}

/* Style for the Firefox slider thumb */
.slider::-moz-range-thumb {
  width: 15%;
  height: 25px;
  background: #074a7d;
  cursor: pointer;
  border-radius: 10px;
}

/* Style for the answer container */
.answer_container {
  display: flex;
  flex-direction: column;
  width: 80%;
  margin-top: 15px;
  margin-bottom: 15px;
}

.columns{
  display: flex;
}
.column.left{
  width: 75%;
  margin-right: 10px;
}
.column.right{
  width: 25%;
  align-items: center;
}

.answer_container h5 {
  margin: 0;
  font-size: 25px;
}

/* Style for the answer text */
.answer_container p {
  font-size: 16px;
}

.source-list {
  list-style-type: none;
  padding: 0;
}

.source-list li {
  margin-bottom: 5px;
}

.source-list a {
  color: #074a7d;
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}
.chat-input-container {
  position: fixed;       /* Fixes the container to the viewport */
  bottom: 10px;             /* Positions it at the bottom of the viewport */
  display: flex;
  width: 80%;
}
.chat-input-wrapper {
  display: flex;
  //align-items: center;
  float: right;
  width: 800px;
  border: 1px solid #ddd;
  border-radius: 25px;
  padding: 10px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Поле ввода */
.chat-input {
  flex: 1;
  border: none;
  border-radius: 20px;
  padding: 10px;
  font-size: 16px;
  resize: none; /* Отключить изменение размеров вручную */
  outline: none;
  overflow-y: auto;
  max-height: 150px; /* Максимальная высота */
}

/* Кнопка отправки */
.send-button {
  background-color: #074a7d;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  margin-left: 10px;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Значок на кнопке отправки */
.send-button svg {
  width: 18px;
  height: 18px;
}

footer{
  height: 100px;
  width: 100%;
}
</style>
