/* tslint:disable:object-literal-key-quotes */
import {Component, OnInit} from '@angular/core';
import {DomSanitizer, SafeHtml} from '@angular/platform-browser';
import {HttpClient} from '@angular/common/http';
import {interval} from 'rxjs';
import { Router } from '@angular/router';

declare var map: any;

@Component({
  selector: 'app-panel',
  templateUrl: './panel.component.html',
  styleUrls: ['./panel.component.css']
})
export class PanelComponent implements OnInit {
  plots = [];
  svg: SafeHtml;
  panelType = 0;
  tasks = [];
  executions = [];
  map;
  localizations = [];
  selectedExecutions = [];
  sub = interval(1000).subscribe(() => { window.dispatchEvent(new Event('resize')); });
  username = sessionStorage.getItem('username');

  taskKeyMapping = [
    ['id', 'Task ID'],
    ['taskName', 'Task name'],
    ['site', 'Site'],
    ['offersType', 'Offers type'],
    ['regions', 'Regions'],
    ['localizations', 'Localizations'],
    ['firstRun', 'Date of first scrapping '],
    ['nextRun', 'Date of next scrapping '],
    ['recurring', 'Recurring'],
  ];

  executionKeyMapping = [
    ['id', 'Task execution ID'],
    ['parent_planned_task_id', 'Task ID'],
    ['runStart', 'Date of scrapping'],
    ['status', 'Current status'],
  ];

  constructor(private http: HttpClient, private sanitizer: DomSanitizer, private router: Router) {
  }

  ngOnInit(): void {
    this.menuClick(0);
    this.getTasks();
    this.getExecutions();
  }

  getById(id) {
    return (<HTMLInputElement> document.getElementById(id)).value;
  }

  renderButtonClick(): void {
    let executions_uuids = [];

    this.selectedExecutions.forEach((element) => {
      executions_uuids.push(this.executions[element]['id']);
    });

    this.http.post('http://127.0.0.1:8000/charts/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'getCharts',
        'requestData': {
          'executedTasks': executions_uuids.toString(),
          'localization': this.getById('locNameIn'),
        }
      })
      .subscribe(
        (val) => {
          this.plots = [];
          for (let key of Object.keys(val)) {
            this.plots.push([key, this.sanitizer.bypassSecurityTrustHtml(val[key])]);
          }},
        () => {},
        () => {}
      );
  }

  clickExecution(index): void {
    if (this.selectedExecutions.includes(index)) {
      this.selectedExecutions = this.selectedExecutions.filter(
        obj => obj !== index
      );
    } else {
      this.selectedExecutions.push(index);
    }
  }

  deleteTask(event): void {
    let id = Number(event.target.closest('button').id.replace('delTaskId:', ''));
    id = this.tasks[id]['id'];

    this.http.post('http://127.0.0.1:8000/tasks/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'deleteTask',
        'requestData': {
          'id': id
        }
      })
      .subscribe(
        () => {this.getTasks(); },
        () => {},
        () => {}
      );
  }

  getTasks(): void {
    this.http.post('http://127.0.0.1:8000/tasks/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'getPlannedTasks',
        'requestData': {}
      })
      .subscribe(
        (val) => {
          this.tasks = <any>val;
          },
        () => {},
        () => {}
        );
  }

  getExecutions(): void {
    this.http.post('http://127.0.0.1:8000/executed_tasks/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'getExecutedTasks',
        'requestData': {}
      })
      .subscribe(
        (val) => {
          console.log(val);
          this.executions = <any> val; },
        () => {},
        () => {}
      );
  }

  menuClick(arg): void {
    const pages = ['page0', 'page1'];
    this.panelType = arg;

    for (let page of pages) {
      const x = document.getElementById(page);
      x.style.display = 'none';
    }

    const x = document.getElementById(pages[arg]);
    x.style.display = 'block';
  }

  newLocalizationButtonClick(): void {
    const newLocalization = (<HTMLInputElement> document.getElementById('newLocalizationIn')).value;

    if (!(this.localizations.some(x => x === newLocalization)) && String(newLocalization).length > 0) {
      this.localizations.push(newLocalization);
    }
  }

  deletelocalizationButtonClick(event): void {
    this.localizations = this.localizations.filter(
      obj => obj !== event.target.closest('button').id.replace('DeleteButton', '')
    );
  }

  addtaskButtonClick(): void {

    this.http.post('http://127.0.0.1:8000/tasks/',
      {
        'username': sessionStorage.getItem('username'),
        'password': sessionStorage.getItem('password'),
        'requestType': 'setNewTask',
        'requestData': {
          'taskName': this.getById('taskNameIn'),
          'site': this.getById('siteIn'),
          'offersType': this.getById('offersTypeIn'),
          'regions': map.selectedRegions.toString(),
          'localizations': this.localizations.toString(),
          'firstRun': this.getById('datetimeIn'),
          'recurring': this.getById('recurringIn'),
          'status': 'waiting',
          'nextRun': this.getById('datetimeIn'),
        }
      })
      .subscribe(
        () => {},
        () => {},
        () => {}
        );

    setTimeout(() => {
      this.getTasks();
    }, 1000);

  }

  logoutButtonClick(): void {
    sessionStorage.setItem('username', 'null');
    sessionStorage.setItem('password', 'null');
    this.router.navigate(['/login']);
  }

}
