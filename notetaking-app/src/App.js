import React, { useState } from 'react';
import Container from '@mui/material/Container';
import NoteForm from './NoteForm';
import NoteList from './NoteList';
import Header from './Header';
import Footer from './Footer';

function App() {
  const [notes, setNotes] = useState([]);
  const [editingNote, setEditingNote] = useState(null);

  const handleAddNote = (note) => {
    setNotes([...notes, { ...note, id: Date.now() }]);
  };

  const handleDeleteNote = (id) => {
    setNotes(notes.filter((note) => note.id !== id));
    if (editingNote && editingNote.id === id) {
      setEditingNote(null);
    }
  };

  const handleEditNote = (note) => {
    setEditingNote(note);
  };

  const handleUpdateNote = (updatedNote) => {
    setNotes(notes.map((note) => (note.id === updatedNote.id ? updatedNote : note)));
    setEditingNote(null);
  };

  return (
    <>
      <Header />
      <Container maxWidth="sm" sx={{ minHeight: '80vh' }}>
        <NoteForm 
          onAddNote={handleAddNote} 
          onUpdateNote={handleUpdateNote} 
          editingNote={editingNote} 
        />
        <NoteList 
          notes={notes} 
          onDelete={handleDeleteNote} 
          onEdit={handleEditNote} 
        />
      </Container>
      <Footer />
    </>
  );
}

export default App;
