import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Link from 'next/link';
import Image from 'next/image';
import ThemeToggle from './ThemeToggle';

export default function Header({ mode, setColorMode }: { mode?: string; setColorMode?: (mode: string) => void }) {
  return (
    <AppBar
      position="sticky"
      color="inherit"
      elevation={0}
      sx={{
        borderBottom: 1,
        borderColor: 'divider',
        top: 0,
        zIndex: (theme) => theme.zIndex.drawer + 1
      }}
    >
      <Toolbar className="flex justify-between">
        <div className="flex items-center gap-2">
          <Link href="/">
            <Image src="/file.svg" alt="Aloha Dental Logo" width={40} height={40} />
          </Link>
          <Typography variant="h6" color="inherit" noWrap>Aloha Dental</Typography>
        </div>
        <nav className="flex gap-4 items-center">
          <Link href="#about" passHref legacyBehavior>
            <Button color="inherit">About</Button>
          </Link>
          <Link href="#services" passHref legacyBehavior>
            <Button color="inherit">Services</Button>
          </Link>
          <Link href="#contact" passHref legacyBehavior>
            <Button color="inherit">Contact</Button>
          </Link>
          <Link href="#appointment" passHref legacyBehavior>
            <Button variant="contained" color="primary">Book Appointment</Button>
          </Link>
          {mode && setColorMode ? (
            <ThemeToggle mode={mode} setColorMode={setColorMode} />
          ) : null}
        </nav>
      </Toolbar>
    </AppBar>
  );
}
