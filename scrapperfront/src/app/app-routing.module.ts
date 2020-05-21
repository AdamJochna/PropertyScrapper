import {BrowserModule} from '@angular/platform-browser';
import {NgModule} from '@angular/core';
import {AppComponent} from './app.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {RouterModule, Routes} from '@angular/router';
import {LoginSiteComponent} from './login-site/login-site.component';
import {Page404Component} from './page404/page404.component';
import {PanelComponent} from './panel/panel.component';
import {HttpClientModule} from '@angular/common/http';
import {RegisterSiteComponent} from './register-site/register-site.component';
import {AuthGuard} from './auth.guard';

const routes: Routes = [
  {
    path: 'login',
    component: LoginSiteComponent
  },
  {
    path: 'register',
    component: RegisterSiteComponent
  },
  {
    path: 'panel',
    component: PanelComponent,
    canActivate: [AuthGuard],
  },
  {
    path: '404',
    component: Page404Component
  },
  {
    path: '**',
    redirectTo: '/login',
  }
];

@NgModule({
  imports: [
    RouterModule.forRoot(routes),
    BrowserModule,
    BrowserAnimationsModule,
    HttpClientModule
  ],
  providers: [AuthGuard],
  bootstrap: [AppComponent],
  exports: [RouterModule]
})

export class AppRoutingModule { }
