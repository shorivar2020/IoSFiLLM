<template>
  <div :class="{'main-centered': !content_exist, 'main-loaded': content_exist}">

    <!-- First slide container for the set of search engines -->
    <SlideSelector v-model="selected" />
    <!-- Textarea for user input and a send button -->
    <div class="chat-input-container">
      <div class="chat-input-wrapper">
        <!-- Input query -->
        <textarea name="message" class="chat-input" v-model="question" placeholder="Enter your question"></textarea>
        <div class="tooltip" data-tooltip="Choose how many sources you need to find">
          <input type="number" id="quantity" name="quantity" v-model="result_number" min="1" max="10" class = "result_number">
        </div>
        <div class="tooltip" data-tooltip="Send question">
          <button class="send-button" @click="sendQuestion">
            <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
              <path d="M2.01 21l20.99-9L2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        <UploadButton @files-uploaded="handleFilesUploaded"/>
      </div>
    </div>

    <FileUpload
      :files_content="files_content"
      :files_name="files_name"
      @remove-file="removeFile"
    />
    <AnswerContainer :loading="loading" :answer="answer" :ai_answer="ai_answer" :source="source" />
    <SourceTable :articles="articles" :source="source" />
    <footer></footer>
  </div>
</template>

<script>
import axios from 'axios' // Importing axios for HTTP requests
import { marked } from 'marked'
import SlideSelector from './components/SlideSelector.vue';
import AnswerContainer from './components/AnswerContainer.vue';
import FileUpload from './components/FileUpload.vue';
import SourceTable from './components/SourceTable.vue';
import UploadButton from './components/UploadButton.vue';
export default {
  data() {
    return {
      question: '',   // Holds the user question input
      result_number: "5",
      answer: '',     // Holds the backend response
      source: '',
      ai_answer: '',
      articles: '',
      selected: "1",    // Value of the first search engine slider
      loading: false,
      content_exist: false,
      fileContent: '',  // To store the file content temporarily
      fileName: 'example.txt',  // File name for the download
      selectedFiles: [],
      files_content: [],
      files_name: [],
    }
  },
  methods: {
    // Function to send the question to the backend
    //'https://legally-full-parakeet.ngrok-free.app/api/check'
    sendQuestion() {
      this.loading = true;
      const contentElements = this.$el.querySelectorAll('.fileContent'); // Fetch all elements
      const content = Array.from(contentElements).map(element => element.innerHTML); // Collect all innerHTMLs
      axios.post('http://127.0.0.1:8080/api/check', {
        question: this.question,
        searchEngine: this.selected,
        fileContent: content,
        resultNumber: this.result_number,
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
    handleFilesUploaded({ files_content, files_name }) {
      // Update the parent component's data with the uploaded files
      this.files_content = files_content;
      this.files_name = files_name;
    },
    removeFile(index) {
    this.files_content.splice(index, 1);
    this.files_name.splice(index, 1);
  },
  },
  computed: {
    filteredArticles() {
      const filter = this.filterGlobal.toLowerCase();
      return this.articles.filter(article => {
        const matchesSource = article.source.toLowerCase().includes(filter);
        const matchesYear = article.year.toString().includes(filter);
        const matchesAuthor = Array.isArray(article.authors)
          ? article.authors.join(", ").toLowerCase().includes(filter)
          : (article.authors || "").toLowerCase().includes(filter);
        const matchesAbstract = article.abstract
          ? article.abstract.toLowerCase().includes(filter)
          : false;

        return matchesSource || matchesYear || matchesAuthor || matchesAbstract;
      });
    },
  },
  components: {
    SlideSelector,
    AnswerContainer,
    FileUpload,
    SourceTable,
    UploadButton
  }

}
</script>

<style scoped>
*{
  font-family: Helvetica, sans-serif;
}
.main-centered {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.main-loaded {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
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
  height: 100%;
}

.send-button:hover {
  opacity: 1;
}

.send-button svg {
  width: 18px;
  height: 18px;
}

.result_number{
  font-size: large;
  border-radius: 20px;
  background: #cdc7c7;
  opacity: 0.7;
  border-style: none;
  height: 100%;
}

/* Chrome, Safari, Edge, Opera */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

/* Firefox */
input[type=number] {
  -moz-appearance: textfield;
}

a:hover {
  opacity: 1;
}

footer{
  height: 50px;
  width: 100%;
}

.tooltip {
  position: relative;
  display: inline-block;
}

.tooltip::after {
  content: attr(data-tooltip);
  visibility: hidden;
  opacity: 0;
  background-color: #333;
  color: #fff;
  text-align: center;
  padding: 5px;
  border-radius: 5px;
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  transition: opacity 0.3s;
  font-size: 12px;
  white-space: nowrap;
}

.tooltip:hover::after {
  visibility: visible;
  opacity: 1;
}

@media only screen and (max-width: 600px) {
  .send-button{
    padding: 6px 8px;
  }

  .send-button svg{
    width: 9px;
    height: 9px;
  }
  .source_container th:first-child, td:first-child {
    width: 50%;
  }
  .filter{
    width: 100%;
  }
  footer{
    display: none;
  }
}
</style>