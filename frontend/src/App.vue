<template>
  <div :class="{'main-centered': !content_exist, 'main-loaded': content_exist}">
    <!-- First slide container for the set of search engines -->
    <div class="slide_container">
      <div class="slide_name">
        <!-- Update the span to reflect the selected engine by adding 'active' class -->
        <span :class="{ active: selected === '1' }">Google</span>
        <span :class="{ active: selected === '2' }">DuckDuckGo</span>
        <span :class="{ active: selected === '3' }">Bing</span>
        <span :class="{ active: selected === '4' }">Brave</span>
        <span :class="{ active: selected === '5' }">Google Scholar</span>
        <span :class="{ active: selected === '6' }">Pub Med</span>
      </div>
      <!-- Range slider bound to 'selected' -->
      <input type="range" min="1" max="6" v-model="selected" class="slider" id="myRange">
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
        <DownloadComponent></DownloadComponent>
        </div>
    </div>

    <div class="answer_container">
      <div v-if="loading" class="loader-wrapper">
        <div v-if="loading" class="loader"></div>
      </div>

      <div v-if="answer" class="answer-input-wrapper">
        <h5>Answer with context</h5>
        <div v-if="answer">
            <div v-html="answer" class="answer"></div>
        </div>
        <p v-else>Wait answer...</p>
        <h5>AI answer without context</h5>
        <div v-if="ai_answer" class = "ai_answer">-->
          <div v-html="ai_answer" class="ai-answer"></div>
        </div>
        <p v-else>Wait AI answer...</p>
      </div>
    </div>

    <div v-if="source" class="source_container">
      <table>
        <thead>
          <tr>
            <th>
              <input type="text" id="filterTitle" v-model="filterTitle" placeholder="Enter title keyword">
              <input type="number" id="filterYear" v-model="filterYear" placeholder="Enter year">
            </th>
            <th>
              <input type="text" id="filterAuthor" v-model="filterAuthor" placeholder="Enter author name">
            </th>
          </tr>
          <tr>
            <th>Source</th>
            <th>Abstract</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(article, index) in filteredArticles" :key="index">
            <td>
              <a :href="article.url" target="_blank" rel="noopener noreferrer">{{ article.source }}</a>
              <p>{{article.year}}</p>
            </td>
            <td>
              <p>{{ article.abstract }}</p>
              <p v-if="article.authors"> Authors: {{ article.authors}}</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <footer> </footer>
  </div>

</template>

<script>
import axios from 'axios' // Importing axios for HTTP requests
import { marked } from 'marked'
import DownloadComponent from "@/components/DownloadComponent.vue";
export default {
  components: {
        DownloadComponent
  },
  data() {
    return {
      question: '',   // Holds the user question input
      answer: '',     // Holds the backend response
      source: '',
      ai_answer: '',
      articles: '',
      selected: "1",    // Value of the first search engine slider
      loading: false,
      content_exist: false,
      filterYear: '',    // Filter year input
      filterAuthor: '',  // New filter for author
      filterTitle: '',
      fileContent: '',  // To store the file content temporarily
      fileName: 'example.txt',  // File name for the download
    }
  },
  methods: {
    // Function to send the question to the backend
    //'https://legally-full-parakeet.ngrok-free.app/api/check'
    sendQuestion() {
      this.loading = true;
      const contentElement = this.$el.querySelector('.fileContent'); // Fetch the element
      const content = contentElement ? contentElement.innerHTML : '';
      axios.post('https://legally-full-parakeet.ngrok-free.app/api/check', {
        question: this.question,
        searchEngine: this.selected,
        fileContent: content,
      })
      .then(response => {
        this.content_exist = true;
        console.log('Response from server:', response.data);
        this.answer = marked.parse(response.data.answer);
        this.source = response.data.source;
        this.ai_answer = marked.parse(response.data.ai_answer);
        this.articles = response.data.articles.map(article => ({
        source: article.title || 'No source available',
        url: article.link || 'No link available',
        authors: article.author || '',
        year: article.year || '',
        abstract: article.abstract || '',
      }));
      })
      .catch(error => {
        console.error('Error:', error);
      })
      .finally(() => {
      this.loading = false;
      });
    },
  },
  computed: {
    filteredArticles() {
      return this.articles.filter(article => {
        const matchesYear = this.filterYear ? article.year == this.filterYear : true;
         const matchesAuthor = this.filterAuthor
        ? (Array.isArray(article.authors)
            ? article.authors.join(', ').toLowerCase().includes(this.filterAuthor.toLowerCase())
            : (article.authors || '').toLowerCase().includes(this.filterAuthor.toLowerCase()))
        : true;
         const matchesTitle = this.filterTitle
        ? article.source.toLowerCase().includes(this.filterTitle.toLowerCase())
        : true;
        return matchesYear && matchesAuthor && matchesTitle;
      });
    },
  },

}
</script>

<style scoped>
.main-centered {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.main-loaded {
  font-family: DM Sans,sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
.loader-wrapper{
  display: flex;
  justify-content: center;
  align-items: center;
}
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
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
}

/* Style for the slider labels (search engine names) */
.slide_name {
  display: flex;
  justify-content: space-between;
  padding-top: 15px;
  width: 80%;
}

/* Style for each individual label */
.slide_name span {
  width: 16%;
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
  width: 16%;
  height: 25px;
  background: #000000;
  cursor: pointer;
  border-radius: 10px;
}

/* Style for the Firefox slider thumb */
.slider::-moz-range-thumb {
  width: 16%;
  height: 25px;
  background: #000000;
  cursor: pointer;
  border-radius: 10px;
}

/* Style for the answer container */
.answer_container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  margin-top: 15px;
  margin-bottom: 15px;

}
.answer-input-wrapper {
  //display: flex;
  //align-items: center;
  width: 800px;
  padding: 10px;
  background-color: white;
}

.answer_container h5 {
  margin: 0;
  font-size: 25px;
}

/* Style for the answer text */
.answer_container p {
  font-size: 16px;
}

.source-list li {
  margin-bottom: 5px;
}

.source-list a {
  color: #000000;
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}
.chat-input-container {
  padding: 10px;
  margin: 10px;
  justify-content: center;
  //position: fixed;       /* Fixes the container to the viewport */
  //bottom: 10px;             /* Positions it at the bottom of the viewport */
  display: flex;
  width: 80%;
}
.chat-input-wrapper {
  display: flex;
  //align-items: center;
  width: 800px;
  border: 1px solid #ddd;
  border-radius: 15px;
  padding: 10px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  border-radius: 20px;
  padding: 10px;
  font-size: 16px;
  resize: none;
  outline: none;
  overflow-y: auto;
  max-height: 150px;
}

.send-button {
  background-color: #000000;
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
    opacity: 0.7;
  transition: opacity .2s;
}

.send-button:hover {
  opacity: 1;
}

.send-button svg {
  width: 18px;
  height: 18px;
}

.source_container{
  display: flex;
  justify-content: center;
  margin-top: 15px;
  margin-bottom: 15px;
}

.source_container table{
  width: 80%;
  border: 1px solid #ddd;
  border-radius: 15px;
  //padding-top: 10px;
  //padding-bottom: 10px;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  table-layout: fixed;
}

.source_container a{
  text-decoration: none;
  color: #000000;
  opacity: 0.7;
  transition: opacity .2s;
}

a:hover {
  opacity: 1;
}

thead {
  position: sticky;
  top: 0;
  z-index: 1;

}

tbody{
  max-height: 400px;
  display: block;
  overflow-y: auto;
  //display: flex;
  //flex-direction: column;
}

tr:nth-child(even) {
  background-color: #cdc7c7;
}

.source_container td{
  padding: 10px;
  word-wrap: break-word;
}

tr{
  display: table;
  width: 100%;
  table-layout: fixed;
  border-bottom: 1px solid #ddd;
  border-radius: 15px;
}

footer{
  height: 50px;
  width: 100%;
}

.loader {
  border: 10px solid #d3d3d3;
  border-top: 10px solid #000000;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
