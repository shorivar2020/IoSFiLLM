<template>
  <div v-if="files_content">
    <div v-for="(content, index) in files_content" :key="index">
      <p>
        <strong>Personal file: </strong> {{ files_name[index] }}
        <button @click="removeFile(index)" class="remove-button">✖</button>
      </p>
      <div v-html="content" class="fileContent"></div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['files_content', 'files_name'],
  methods: {
    removeFile(index) {
      this.$emit('remove-file', index);
    }
  }
};
</script>

<style scoped>
/* FileUpload component styles */
.fileContent{
  display: none;
}

.remove-button{
  background-color: #000000;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  margin-left: 10px;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.7;
  transition: opacity .2s;
}

.remove-button:hover {
  opacity: 1;
}
</style>
