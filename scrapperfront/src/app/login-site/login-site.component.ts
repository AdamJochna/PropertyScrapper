import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {HttpClient} from '@angular/common/http';

@Component({
  selector: 'app-login-site',
  templateUrl: './login-site.component.html',
  styleUrls: ['./login-site.component.css']
})
export class LoginSiteComponent implements OnInit {
  errorFlag = false;

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit(): void {
  }

  signInButton() {
    const login = (<HTMLInputElement> document.getElementById('usernameFieldLogin')).value;
    const password = (<HTMLInputElement> document.getElementById('passwordFieldLogin')).value;

    this.http.post('http://127.0.0.1:8000/users/',
      {
        'username': login,
        'password': password,
        'requestType': 'loginUser',
        'requestData': {}
      })
      .subscribe(
        (val) => {
          if(val['log'] === 'success') {
            sessionStorage.setItem('username', login);
            sessionStorage.setItem('password', password);
            this.router.navigate(['/panel']);
          }
          else{
            this.errorFlag = true;
          }
        },
        response => {},
        () => {});

  }

    registerButton() {
      this.router.navigate(['/register']);
    }



}
