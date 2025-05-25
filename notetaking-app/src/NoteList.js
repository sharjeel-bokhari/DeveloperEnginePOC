import React from 'react';
import Note from './Note';
import List from '@mui/material/List';

const NoteList = ({ notes, onDelete, onEdit }) => {
  if (!notes.length) {
    return <div style={{textAlign: 'center', color: '#888'}}>No notes yet. Add one!</div>;
  }
  return (
    <List>
      {notes.map((note, index) => (
        <Note
          key={note.id}
          note={note}
          onDelete={onDelete}
          onEdit={onEdit}
          index={index}
        />
      ))}
    </List>
  );
};

export default NoteList;
