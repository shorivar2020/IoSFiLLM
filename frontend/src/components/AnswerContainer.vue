<template>
  <div class="answer-container">
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
          <div v-html="ai_answer" class="ai_answer"></div>
        </div>
        <p v-else>Wait AI answer...</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['loading', 'answer', 'ai_answer', 'source'],
};
</script>

<style scoped>

.loader {
  border: 10px solid #d3d3d3;
  border-top: 10px solid #000000;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 2s linear infinite;
}
/* Style for the answer container */
.answer_container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  margin-top: 15px;
  margin-bottom: 15px;
  align-items: center;

}
.answer-input-wrapper {
  //display: flex;
  //align-items: center;
  align-items: center;
  width: 80%;
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

.answer p a{
  text-decoration: none;
  color: black;
  font-weight: bold;
}

/* Style for the answer container */
.answer_container {
  display: flex;
  justify-content: center;
  flex-direction: column;
  margin-top: 15px;
  margin-bottom: 15px;
  align-items: center;

}
.answer-input-wrapper {
  //display: flex;
  //align-items: center;
  align-items: center;
  width: 80%;
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

.answer p a{
  text-decoration: none;
  color: black;
  font-weight: bold;
}

.loader-wrapper{
  display: flex;
  justify-content: center;
  align-items: center;
}

@media only screen and (max-width: 600px) {
  .slide_name{
    font-size: 10px;
  }

  .send-button{
    padding: 6px 8px;
  }

  .send-button svg{
    width: 9px;
    height: 9px;
  }

  .answer-input-wrapper{
    width: 80%;
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


@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>
