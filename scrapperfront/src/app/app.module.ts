import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginSiteComponent } from './login-site/login-site.component';
import { Page404Component } from './page404/page404.component';
import { PanelComponent } from './panel/panel.component';
import { RegisterSiteComponent } from './register-site/register-site.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginSiteComponent,
    Page404Component,
    PanelComponent,
    RegisterSiteComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
