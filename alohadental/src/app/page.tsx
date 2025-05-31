"use client";
import * as React from "react";
import { useRouter } from "next/navigation";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
import Stack from "@mui/material/Stack";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy authentication logic
    if (email && password) {
      setError("");
      router.push("/home");
    } else {
      setError("Please enter both email and password.");
    }
  };

  return (
    <Box sx={{ minHeight: "80vh", display: "flex", alignItems: "center", justifyContent: "center", bgcolor: "background.default" }}>
      <Container maxWidth="xs">
        <Paper elevation={4} sx={{ p: 4, borderRadius: 4 }}>
          <Typography variant="h4" align="center" sx={{ mb: 2, fontWeight: 700, color: "primary.main" }}>
            Sign In
          </Typography>
          <Typography variant="body1" align="center" sx={{ mb: 4, color: "text.secondary" }}>
            Welcome back! Please sign in to continue.
          </Typography>
          <Box component="form" onSubmit={handleSubmit} noValidate>
            <Stack spacing={3}>
              <TextField
                label="Email"
                variant="outlined"
                type="email"
                required
                autoComplete="email"
                fullWidth
                value={email}
                onChange={e => setEmail(e.target.value)}
              />
              <TextField
                label="Password"
                variant="outlined"
                type="password"
                required
                autoComplete="current-password"
                fullWidth
                value={password}
                onChange={e => setPassword(e.target.value)}
              />
              {error && <Typography color="error" variant="body2">{error}</Typography>}
              <Button type="submit" variant="contained" size="large" color="primary" sx={{ borderRadius: 3 }} fullWidth>
                Sign In
              </Button>
            </Stack>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
