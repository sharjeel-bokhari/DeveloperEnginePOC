import React, { useState, useEffect } from 'react';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Paper from '@mui/material/Paper';
import Stack from '@mui/material/Stack';

const NoteForm = ({ onAddNote, onUpdateNote, editingNote }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  useEffect(() => {
    if (editingNote) {
      setTitle(editingNote.title);
      setContent(editingNote.content);
    } else {
      setTitle('');
      setContent('');
    }
  }, [editingNote]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() && !content.trim()) return;
    if (editingNote) {
      onUpdateNote({ ...editingNote, title, content });
    } else {
      onAddNote({ title, content });
    }
    setTitle('');
    setContent('');
  };

  return (
    <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
      <form onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <TextField
            label="Title"
            variant="outlined"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
            required
          />
          <TextField
            label="Content"
            variant="outlined"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            multiline
            minRows={3}
            fullWidth
            required
          />
          <Button type="submit" variant="contained" color="primary">
            {editingNote ? 'Update Note' : 'Add Note'}
          </Button>
        </Stack>
      </form>
    </Paper>
  );
};

export default NoteForm;
