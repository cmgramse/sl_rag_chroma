const express = require('express');
const multer = require('multer');
const pdf = require('pdf-parse');
const { Configuration, OpenAIApi } = require("openai");

const app = express();
const upload = multer({ dest: 'uploads/' });

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

let pdfContent = '';

app.use(express.json());
app.use(express.static('public'));

app.post('/upload', upload.single('pdf'), (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  pdf(req.file.buffer).then(function(data) {
    pdfContent = data.text;
    res.send('PDF uploaded and processed successfully.');
  });
});

app.post('/query', async (req, res) => {
  if (!pdfContent) {
    return res.status(400).send('No PDF content available. Please upload a PDF first.');
  }

  const query = req.body.query;
  if (!query) {
    return res.status(400).send('No query provided.');
  }

  try {
    const response = await openai.createCompletion({
      model: "text-davinci-002",
      prompt: `Based on the following content:\n\n${pdfContent}\n\nAnswer this question: ${query}`,
      max_tokens: 150
    });

    res.json({ answer: response.data.choices[0].text.trim() });
  } catch (error) {
    console.error(error);
    res.status(500).send('An error occurred while processing your query.');
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running on port ${port}`));