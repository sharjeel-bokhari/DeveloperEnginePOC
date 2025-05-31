"use client";
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import TextField from '@mui/material/TextField';
import Stack from '@mui/material/Stack';

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <Paper
        elevation={0}
        sx={{
          background: 'linear-gradient(135deg, #e3f2fd 0%, #fce4ec 100%)',
          py: { xs: 8, md: 12 },
          mb: 6,
          minHeight: { xs: 400, md: 480 },
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={6} alignItems="center" justifyContent="center">
            <Grid item xs={12} md={8}>
              <Typography variant="h2" component="h1" sx={{ fontWeight: 800, mb: 3, color: '#111' }} gutterBottom>
                Welcome to Aloha Dental
              </Typography>
              <Typography variant="h5" component="p" sx={{ mb: 4, color: '#222' }}>
                Your family’s smile is our top priority. Experience gentle, modern dental care in a friendly environment.
              </Typography>
              <Button
                variant="contained"
                color="primary"
                size="large"
                href="#appointment"
                sx={{ borderRadius: 6, px: 4, py: 1.5, fontWeight: 600 }}
              >
                Book an Appointment
              </Button>
            </Grid>
          </Grid>
        </Container>
      </Paper>

      {/* About Section */}
      <Container id="about" maxWidth="md" sx={{ py: 8 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }} gutterBottom>
          About Us
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Aloha Dental has been serving the community with exceptional dental care for over 20 years. Our experienced team is dedicated to providing personalized, gentle care in a relaxing atmosphere.
        </Typography>
        <Typography variant="body1">
          We offer a full range of dental services for patients of all ages, using the latest technology and techniques to ensure your comfort and satisfaction.
        </Typography>
      </Container>

      {/* Services Section */}
      <Box id="services" sx={{ bgcolor: 'grey.100', py: 8 }}>
        <Container maxWidth="lg">
          <Typography variant="h4" component="h2" sx={{ fontWeight: 700, mb: 3, color: 'primary.main' }} gutterBottom>
            Our Services
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, borderRadius: 4, textAlign: 'center', height: '100%' }}>
                <img src="/vercel.svg" width={60} height={60} alt="Preventive Care" style={{ marginBottom: 16 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>Preventive Care</Typography>
                <Typography variant="body2" color="text.secondary">
                  Regular exams, cleanings, and oral hygiene education to keep your smile healthy.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, borderRadius: 4, textAlign: 'center', height: '100%' }}>
                <img src="/window.svg" width={60} height={60} alt="Restorative Dentistry" style={{ marginBottom: 16 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>Restorative Dentistry</Typography>
                <Typography variant="body2" color="text.secondary">
                  Fillings, crowns, and bridges to restore function and aesthetics to your teeth.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper elevation={2} sx={{ p: 4, borderRadius: 4, textAlign: 'center', height: '100%' }}>
                <img src="/next.svg" width={60} height={60} alt="Cosmetic Dentistry" style={{ marginBottom: 16 }} />
                <Typography variant="h6" sx={{ mb: 1 }}>Cosmetic Dentistry</Typography>
                <Typography variant="body2" color="text.secondary">
                  Teeth whitening, veneers, and more for a beautiful, confident smile.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Contact Section */}
      <Container id="contact" maxWidth="md" sx={{ py: 8 }}>
        <Typography variant="h4" component="h2" sx={{ fontWeight: 700, mb: 2, color: 'primary.main' }} gutterBottom>
          Contact Us
        </Typography>
        <Typography variant="body1" sx={{ mb: 2 }}>
          Call us at <a href="tel:1234567890" style={{ color: '#1976d2', textDecoration: 'underline' }}>(123) 456-7890</a> or email <a href="mailto:info@alohadental.org" style={{ color: '#1976d2', textDecoration: 'underline' }}>info@alohadental.org</a>
        </Typography>
        <Typography variant="body1">
          123 Aloha St, Honolulu, HI 96815
        </Typography>
      </Container>

      {/* Appointment Section */}
      <Box id="appointment" sx={{ bgcolor: 'background.default', py: 8 }}>
        <Container maxWidth="sm">
          <Paper elevation={3} sx={{ p: { xs: 3, md: 5 }, borderRadius: 4, boxShadow: 4 }}>
            <Typography variant="h4" component="h2" sx={{ fontWeight: 700, mb: 3, color: 'primary.main' }} gutterBottom align="center">
              Book Your Appointment
            </Typography>
            <Box
              component="form"
              noValidate
              autoComplete="off"
              sx={{ mt: 2 }}
              className="flex flex-col gap-4 items-center"
            >
              <Stack spacing={3} width="100%">
                <TextField fullWidth label="Name" name="name" variant="outlined" required />
                <TextField fullWidth label="Email" name="email" type="email" variant="outlined" required />
                <TextField fullWidth label="Phone" name="phone" type="tel" variant="outlined" required />
                <TextField fullWidth label="Your message" name="message" multiline rows={4} variant="outlined" />
                <Button type="submit" variant="contained" color="primary" size="large" sx={{ borderRadius: 4 }}>
                  Submit
                </Button>
              </Stack>
            </Box>
          </Paper>
        </Container>
      </Box>
    </>
  );
}
