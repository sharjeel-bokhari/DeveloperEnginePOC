import Typography from '@mui/material/Typography';
import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="bg-gray-100 py-6 mt-12 border-t">
      <div className="max-w-5xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center">
        <Typography variant="body2" color="text.secondary" align="center">
          {'© '}
          {new Date().getFullYear()} Aloha Dental. All rights reserved.
        </Typography>
        <div className="flex gap-4 mt-2 md:mt-0">
          <Link href="#privacy" className="text-sm text-gray-600 hover:underline">Privacy Policy</Link>
          <Link href="#terms" className="text-sm text-gray-600 hover:underline">Terms of Service</Link>
        </div>
      </div>
    </footer>
  );
}
