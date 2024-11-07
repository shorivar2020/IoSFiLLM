<template>
  <!-- First slide container for the first set of search engines -->
  <div class="grid-container">
    <div class="grid-item item1">
      <div class="slide_container">
        <div class="slide_name">
          <!-- Update the span to reflect the selected engine by adding 'active' class -->
          <span :class="{ active: selected === 1 }">Google</span>
          <span :class="{ active: selected === 2 }">Google Schoolar</span>
          <span :class="{ active: selected === 3 }">DuckDuckGo</span>
          <span :class="{ active: selected === 4 }">Bing</span>
          <span :class="{ active: selected === 5 }">Brave</span>
          <span :class="{ active: selected === 6 }">Google api</span>
        </div>
        <!-- Range slider bound to 'selected' -->
        <input type="range" min="1" max="6" v-model="selected" class="slider" id="myRange">
      </div>

      <!-- Second slide container for the second set of search engines -->
      <div class="slide_container">
        <div class="slide_name">
          <!-- Update the span to reflect the selected engine by adding 'active2' class -->
          <span :class="{ active2: selected2 === 1 }">Gemini</span>
          <span :class="{ active2: selected2 === 2 }">ChatGPT</span>
          <span :class="{ active2: selected2 === 3 }">Bing</span>
        </div>
        <!-- Range slider bound to 'selected2' -->
        <input type="range" min="1" max="3" v-model="selected2" class="slider" id="myRange2">
      </div>
    </div>
    <!-- Answer container for displaying the backend response -->
    <div class="grid-item item2">
      <div class="answer_container">
        <div>
          <ul v-if="source.length > 0" class="source-list">
            <li><p>Sources:</p></li>
            <li v-for="(url, index) in source" :key="index">
              <a :href="url" target="_blank" rel="noopener noreferrer">{{ getDomain(url) }}</a>
            </li>
          </ul>
          <p v-else>Wait source...</p>
        </div>
      </div>
    </div>
    <div class="grid-item item3">
      <div class="answer_container">
        <p v-if="answer">Answer: {{ answer }}</p>
        <!-- Placeholder text before getting a real answer -->
        <p v-else>Wait answer...</p>
      </div>
    </div>
    <div class="grid-item item4">
      <div class="answer_container">
          <p v-if="ai_answer">AI: {{ ai_answer }}</p>
          <!-- Placeholder text before getting a real answer -->
          <p v-else>Wait answer...</p>
      </div>
    </div>
    <div class="grid-item item5">
      <!-- Textarea for user input and a send button -->
      <div class="textarea_container">
        <textarea name="message" rows="10" cols="30" v-model="question" placeholder="Enter your question"></textarea>
        <button @click="sendQuestion">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios' // Importing axios for HTTP requests

export default {
  data() {
    return {
      question: '',   // Holds the user question input
      answer: '',     // Holds the backend response
      source: '',
      ai_answer: '',
      selected: 1,    // Value of the first search engine slider
      selected2: 1    // Value of the second search engine slider
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
        aiEngine: this.selected2
      })
      .then(response => {
        console.log('Response from server:', response.data);
        this.answer = response.data.answer;
        this.source = response.data.source;
        this.ai_answer = response.data.ai_answer;
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }

  }
}
</script>

<style scoped>
.grid-container {
  display: grid;
}

.grid-item {
  text-align: center;
}

.item1 {
  grid-column: 1 / span 3;
  grid-row: 1;
}

.item2 {
  grid-column: 3;
  grid-row: 2;
}

.item3 {
  grid-column: 1 / span 2;
  grid-row: 2;
}

.item4 {
  grid-column: 1 / span 3;
  grid-row: 3;
}

.item5 {
  grid-column: 1 / span 3;
  grid-row: 4;
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

/* Style for the textarea container */
.textarea_container {
  text-align: center;
  width: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
}

/* Style for the textarea */
.textarea_container textarea {
  background: #d3d3d3;
  outline: none;
  height: 70px;
  width: 80%;
  border-radius: 10px;
  border: none;
  font-size: 16px;
  resize: none;
}

/* Style for the send button */
.textarea_container button {
  height: 25px;
  width: 20%;
  background: #074a7d;
  cursor: pointer;
  border-radius: 10px;
  color: white;
  margin: 15px;
}

/* Style for the answer container */
.answer_container {
  text-align: center;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: Arial, sans-serif;
}

/* Style for the answer text */
.answer_container p {
  width: 80%;
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
  color: #1e90ff;
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}
</style>
