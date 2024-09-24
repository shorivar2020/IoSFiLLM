<template>
  <div>
    <h1>Введите вопрос:</h1>
    <input v-model="question" placeholder="Введите ваш вопрос" />
    <button @click="sendQuestion">Отправить</button>

    <p v-if="answer">Ответ: {{ answer }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      question: '',  // Вопрос пользователя
      answer: ''     // Ответ от бэкенда
    }
  },
  methods: {
    sendQuestion() {
      // Отправляем вопрос на бэкенд
      axios.post('http://127.0.0.1:5000/api/check', { question: this.question })  // Flask
      // axios.post('http://127.0.0.1:8000/api/check', { question: this.question })  // FastAPI
        .then(response => {
          this.answer = response.data.answer  // Получаем ответ от бэкенда
        })
        .catch(error => {
          console.error('Ошибка при отправке вопроса:', error)
        })
    }
  }
}
</script>

<style scoped>
input {
  margin-right: 10px;
}
button {
  margin-left: 10px;
}
</style>
