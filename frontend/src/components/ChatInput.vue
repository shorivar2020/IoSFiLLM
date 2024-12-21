<template>
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
</template>

<script>
import axios from "axios";
import {marked} from "marked";

export default {
  data() {
    return {
      question: '',   // Holds the user question input
      result_number: "5",
      answer: '',     // Holds the backend response
      source: '',
      ai_answer: '',
      articles: '',
    }
  },
  methods: {
    // Function to send the question to the backend
    //'https://legally-full-parakeet.ngrok-free.app/api/check'
    sendQuestion() {
      this.loading = true;
      const contentElements = this.$el.querySelectorAll('.fileContent'); // Fetch all elements
      const content = Array.from(contentElements).map(element => element.innerHTML); // Collect all innerHTMLs
      axios.post('https://legally-full-parakeet.ngrok-free.app/api/check', {
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
  },
}
</script>

<style>

</style>