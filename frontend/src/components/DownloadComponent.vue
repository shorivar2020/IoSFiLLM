<template>
    <button class="send-button" @click="selectAndUploadFile">
       <img
           src="../../public/upload-sign-svgrepo-com.png"
           alt="Upload_icon"
           width="18px"
           height="18px"
    ></button>

    <input
      type="file"
      ref="fileInput"
      @change="uploadFile"
      style="display: none;"
    />
    <div v-if="uploading">Uploading...</div>
    <div v-if="uploadError" class="popup-overlay">
        <div class="popup-content">
          <p>An error occurred during upload!</p>
          <button @click="uploadError = false">Close</button>
        </div>
      </div>
    <div v-if="fileContent">
      <div v-html="fileContent" class="fileContent"></div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      selectedFile: null,
      uploading: false,
      uploadError: false,
      uploadSuccess: false,
      fileContent: '',
    };
  },
  methods: {
     selectAndUploadFile() {
      // Programmatically trigger file input click
      this.$refs.fileInput.click();
    },
    async uploadFile(event) {
      // Get the file from the input field
      this.selectedFile = event.target.files[0];

      if (!this.selectedFile) {
        alert("Please select a file to upload");
        return;
      }

      const formData = new FormData();
      formData.append('file', this.selectedFile);

      this.uploading = true;
      this.uploadError = false;
      this.uploadSuccess = false;

      try {
        const response = await axios.post('http://127.0.0.1:8080/api/download', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });

        if (response.status === 200) {
          this.uploadSuccess = true;
          console.log('Response from server:', response.data);
          this.fileContent = response.data.file_content;
        }
      } catch (error) {
        this.uploadError = true;
      } finally {
        this.uploading = false;
      }
    },
    handleFileChange(event) {
      // Get the file from the input field
      this.selectedFile = event.target.files[0];
    },

  },
};
</script>

<style scoped>

.fileContent{
  display: none;
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

.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-content {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}
</style>