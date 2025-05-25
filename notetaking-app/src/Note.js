import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';

const Note = ({ note, onDelete, onEdit }) => {
  return (
    <Card sx={{ marginBottom: 2 }}>
      <CardContent>
        <Typography variant="h6">{note.title}</Typography>
        <Typography variant="body2" color="text.secondary">
          {note.content}
        </Typography>
        <IconButton aria-label="edit" onClick={() => onEdit(note)}>
          <EditIcon />
        </IconButton>
        <IconButton aria-label="delete" onClick={() => onDelete(note.id)}>
          <DeleteIcon />
        </IconButton>
      </CardContent>
    </Card>
  );
};

export default Note;
