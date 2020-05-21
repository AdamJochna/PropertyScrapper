import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register-site',
  templateUrl: './register-site.component.html',
  styleUrls: ['./register-site.component.css']
})
export class RegisterSiteComponent implements OnInit {
  verifyEmailSite = 0;
  errorFlag = false;

  constructor(private http: HttpClient, private router: Router) {
  }

  ngOnInit(): void {
  }

  registerButtonClick(): void {
    this.verifyEmailSite = 1;
    sessionStorage.setItem('username', (<HTMLInputElement> document.getElementById('usernameField')).value);
    sessionStorage.setItem('password', (<HTMLInputElement> document.getElementById('passwordField')).value);

    this.http.post('http://127.0.0.1:8000/users/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'registerUser',
        'requestData': {
          'email': (<HTMLInputElement> document.getElementById('emailField')).value,
        }
      })
      .subscribe(
        (val) => {
          console.log('POST call successful value returned in body', val);
        },
        response => {
          console.log('POST call in error', response);
        },
        () => {
          console.log('The POST observable is now completed.');
        });
  }

  verificationCodeButtonClick(): void {
    console.log('siema eniu');

    this.http.post('http://127.0.0.1:8000/users/',
      {
        username: sessionStorage.getItem('username'),
        password: sessionStorage.getItem('password'),
        requestType: 'verifyEmail',
        requestData: {
          verificationCode: (<HTMLInputElement> document.getElementById('verificationCodeField')).value,
        }
      })
      .subscribe(
        (val) => {
          console.log('POST call successful value returned in body', val);
          if (val['log'] === 'success') {
              this.router.navigate(['/login']);
          } else {
            this.errorFlag = true;
          }
        },
        response => {
          console.log('POST call in error', response);
        },
        () => {
          console.log('The POST observable is now completed.');
        });
  }

    loginButtonClick(): void {
      this.router.navigate(['/login']);
    }

}
